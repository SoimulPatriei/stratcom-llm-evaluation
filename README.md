# AI in Support of StratCom: Narrative Detection, Topic Modeling, and Sentiment Analysis with LLMs

This repository contains the code, data, and prompt templates used in the evaluation of large language models (LLMs) for three key NLP tasks: **narrative detection**, **topic modeling**, and **aspect-based sentiment analysis (ABSA)**. The focus of this work is multilingual processing, with an emphasis on English and Latvian texts relevant to Strategic Communication (StratCom).

## 📁 Repository Structure

```
├── Corpora/                  # News and media corpora in English and Latvian
│   ├── English/
│   └── Latvian/
├── Prompting-Templates/     # Prompt templates used for interacting with LLMs
├── Tasks/                   # Scripts and outputs for Narrative Detection, Topic Modeling, and ABSA
```

## 🧠 Evaluated Models

The following large language models were evaluated:

- **GPT-4.0** 
- **Mistral Nemo** 
- **Mistral Large**
- **LLaMA 31-405b**
- **Gemini** 

These models were accessed through public APIs to ensure transparency and reproducibility.

## 🧪 Tasks and Methodology

All models were evaluated in **zero-shot** or **few-shot** settings using task-specific prompts.

- **Narrative Detection**: Extracting key entities, semantic relationships, and narrative structure following Freytag’s Pyramid.
- **Topic Modeling**: Identifying latent topics across multilingual media content using LLM-generated clusters.
- **Aspect-Based Sentiment Analysis (ABSA)**: Extracting target-specific sentiment with structured reasoning.

Evaluations were performed manually by StratCom experts to assess accuracy and contextual relevance, especially in low-resource settings.

## 📄 Report

For an in-depth description of methods, findings, and implications, refer to the full report:

> **AI in Support of StratCom: The Use and Evaluation of Large Language Models in Less-Spoken EU Languages**  
> *Eduard Barbu, Somnath Banerjee, Tanya Lim, Liene Zīvere*  
> NATO Strategic Communications Centre of Excellence, Riga

## 👥 Contributors

- **Eduard Barbu** (University of Tartu, NLP & evaluation coordination, code contribution)  
- **Somnath Banerjee** (LLM prompt engineering & code contributions, evaluation)  
- **Tanya Lim** (Evaluation methodology, English corpus review)  
- **Liene Zīvere** (Evaluation methodology,Latvian corpus review)

## 🔗 Acknowledgments

This work was conducted with the support of the NATO StratCom COE and domain experts in multilingual NLP and strategic communication.