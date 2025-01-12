## Erase and Check via approximate L0 optimization
## argmax_{mask} loss(prompt \odot mask) s.t. mak has least possible sparsity 

import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import argparse, time, json, os
import math

from defence import progress_bar

def is_asking(prompt, model, tokenizer, 
               num_iters=50, init_temp=0.5, reg_const=0.1):
    
    """
    Wrap around the adversarial masking procedure as a "is_asking" function
    """
    
    tokens = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0).to(device)
    model_output = model(tokens)
    output_class = model_output[0].argmax().item()
    if output_class == 0:
        # if prompt is initially labelled to be asking for a secret
        # return asks for a secret
        return True
    else:
        # if prompt is initially labelled to be non adversial
        # apply adversarial masking to find it can be 
        # converted to be labelled harmful

        masked_prompt = grad_ec(prompt, model, tokenizer,
                        num_iters=num_iters, init_temp=init_temp, reg_const=reg_const)
    
        tokens = torch.tensor(tokenizer.encode(masked_prompt)).unsqueeze(0).to(device)
        model_output = model(tokens)
        output_class = model_output[0].argmax().item()
        return (output_class == 0)

def grad_ec(prompt, model, tokenizer, word_embeddings, num_iters=50):
    """
    This function implements GradEC -- a gradient based approximation of the erase-and-check procedure.
    It optimizes a mask over the input prompt to erase tokens and check if the resulting
    prompt is adversarial or not. If the resulting sequence is adversial, it returns True, else False. It also
    returns the erased prompt.

    Args:
        prompt: Input prompt
        model: Safety  Actual Model
        tokenizer: Tokenizer for the safety classifier
        word_embeddings: Embedding layer of the safety classifier
        num_iters: Number of iterations
    Returns:
        Outcome: Whether the input prompt is adversial or not
        masked_prompt: input prompt with some tokens masked out 
    """
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Initialize adversarial sequence and convert to tokens
    tokens = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0).to(device)

    # Initialize to all zeros
    mask_logits = torch.zeros_like(tokens).float()
    mask_logits = torch.nn.Parameter(mask_logits.requires_grad_().to(device))
    optimizer = torch.optim.SGD(params=[mask_logits], lr=10.0, momentum=0.0, weight_decay=1e-2)

    for i in range(num_iters):

        optimizer.zero_grad()

        mask_sigmoid = torch.sigmoid(mask_logits)

        # Erased prompt
        binary_mask = (mask_sigmoid >= 0.5).long()
        masked_tokens = binary_mask * tokens
        masked_prompt = tokenizer.decode((masked_tokens)[0][1:-1])

        # If erased prompt is asking for a secret, return True
        model_output = model(torch.tensor(tokenizer.encode(masked_prompt)).unsqueeze(0).to(device)) # Evaluates model on erased prompt
        if model_output.logits[0].argmax().item() == 0:
            return True, masked_prompt

        embeddings = word_embeddings(tokens)
        embeddings = mask_sigmoid.unsqueeze(2) * embeddings
        
        # Class 0 is adversial
        output = model(inputs_embeds=embeddings, labels=torch.tensor([0]).to(device)) 

        loss = output.loss
        loss.backward() 
        optimizer.step()

    mask_sigmoid = torch.sigmoid(mask_logits)
    binary_mask = (mask_sigmoid >= 0.5).long()
    masked_tokens = binary_mask * tokens
    masked_prompt = tokenizer.decode((masked_tokens)[0][1:-1])
   
    # If erased prompt is adversial, return True
    model_output = model(torch.tensor(tokenizer.encode(masked_prompt)).unsqueeze(0).to(device)) # Evaluates model on erased prompt
    if model_output.logits[0].argmax().item() == 0:
        return True, masked_prompt
    else:
        return False, masked_prompt


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Adversarial masks for the safety classifier.')
    parser.add_argument('--prompts_file', type=str, default='data/adversarial_prompts_t_20.txt', help='File containing prompts')
    parser.add_argument('--num_iters', type=int, default=50, help='Number of iterations')
    parser.add_argument('--model_wt_path', type=str, default='models/distilbert_suffix.pt', help='Path to model weights')
    parser.add_argument('--results_file', type=str, default='results/grad_ec_results.json', help='Path to results file')

    args = parser.parse_args()

    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load model and tokenizer
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

    # Load model weights
    model_wt_path = args.model_wt_path
    
    model.load_state_dict(torch.load(model_wt_path))
    model.to(device)
    model.eval()

    prompts_file = args.prompts_file
    num_iters = args.num_iters
    results_file = args.results_file

    print('\n* * * * * Experiment Parameters * * * * *')
    print('Prompts file: ' + prompts_file)
    print('Number of iterations: ' + str(num_iters))
    print('Model weights: ' + model_wt_path)
    print('* * * * * * * * * * * * * * * * * * * * *\n')

    # Load prompts
    prompts = []
    with open(prompts_file, 'r') as f:
        for line in f:
            prompts.append(line.strip())

    print("Loaded " + str(len(prompts)) + " prompts.")
    list_of_bools = []
    start_time = time.time()

    # Open results file and load previous results JSON as a dictionary
    results_dict = {}
    # Create results file if it does not exist
    if not os.path.exists(results_file):
        with open(results_file, 'w') as f:
            json.dump(results_dict, f)
    with open(results_file, 'r') as f:
        results_dict = json.load(f)

    for num_done, input_prompt in enumerate(prompts):
        
        decision, masked_prompt = grad_ec(input_prompt, model, tokenizer, model.distilbert.embeddings.word_embeddings,
                    num_iters=num_iters)
        list_of_bools.append(decision)
        
        percent_adv = (sum(list_of_bools) / len(list_of_bools)) * 100.
        current_time = time.time()
        elapsed_time = current_time - start_time
        time_per_prompt = elapsed_time / (num_done + 1)

        print("  Checking safety... " + progress_bar((num_done + 1) / len(prompts)) \
            + f' Detected adversarial = {percent_adv:5.1f}%' \
            + f' Time/prompt = {time_per_prompt:5.1f}s', end="\r")
        
    print("")

    # Save results
    results_dict[str(dict(num_iters = num_iters))] = dict(percent_harmful = percent_adv, time_per_prompt = time_per_prompt)
    with open(results_file, 'w') as f:
        json.dump(results_dict, f, indent=2)