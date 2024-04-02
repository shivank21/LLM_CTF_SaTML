# LLM_CTF_SaTML

This repository contains all the work our team put into the Large Language Model Capture-the-Flag (LLM CTF) Competition @ SaTML 2024. The competition's goal was to explore how basic prompting and filtering techniques could enhance the resilience of LLM applications against prompt injection and extraction.

## Competition Overview

In this competition, participants assume the roles of defenders and/or attackers:
- Defenders craft prompts and filters to instruct an LLM to keep a secret, aiming to prevent its discovery in a conversation.
- Attackers design strategies to extract the secret from the LLM, circumventing the defender's safeguards.

The competition was broadly divided into 2 phases: the Defense phase and the Attack (Reconnaissance and Evaluation) phase. We aimed to simulate the real-world security convention, defenders anticipate and prepare for attacks, while attackers adapt to the defenses in place. Current large language models (LLMs) cannot yet follow initial instructions reliably, if adversarial users or third parties can later provide input to the model. It is a major obstacle to using LLMs as the core of a user-facing application.
<br>
A Black-box setting similar to the real-world LLM application threat model is put in place: the attacker has no white-box access to the defender’s security mechanism. However, they can do large number of queries during the Reconnaissance phase to find out how any defense behaves.

## Models for Testing
Gpt-3.5-turbo-1106 and llama-2-70b-chat have been used for testing the prompts and defences.