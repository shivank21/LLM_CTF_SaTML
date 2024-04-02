# Defences 
![image](https://github.com/shivank21/LLM_CTF_SaTML/assets/143031293/dfa39e15-9cd8-4c30-9251-21dc7fb48b71)

A useful way of defending our model from outputting known secrets is by using [LLM Guard](https://github.com/protectai/llm-guard?tab=readme-ov-file), specifically [ban_substrings](https://llm-guard.com/output_scanners/ban_substrings/) by adding them into the BanSubstrings class of llm-guard.

Another approach that we use is based upon [Certifying LLM Safety against Adversarial Prompting](https://arxiv.org/pdf/2309.02705.pdf) where a novel erase-and-check method was proposed to check the adversarial robustness of a language model

![image](https://github.com/shivank21/vlg-recruitment-1y/assets/128126577/a9dc9e22-534a-417d-8fe3-693352b8b047)

Here, we modify the code so that rather than checking that a prompt is safe or not we rather check if the prompt is asking for the secret or not and greedily erase the tokens that maximize the softmax scores of the classes asking for the secret.
