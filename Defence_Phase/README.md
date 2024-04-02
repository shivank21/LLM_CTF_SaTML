# Defences 
![image](https://github.com/shivank21/LLM_CTF_SaTML/assets/143031293/dfa39e15-9cd8-4c30-9251-21dc7fb48b71)

A useful way of defending our model from outputting known secrets is by using [LLM Guard](https://github.com/protectai/llm-guard?tab=readme-ov-file), specifically [ban_substrings](https://llm-guard.com/output_scanners/ban_substrings/) by adding them into the BanSubstrings class of llm-guard
