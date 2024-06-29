# DA-Code: Agent Data Science Code Generation Benchmark for Large Language Models

## ⚙️ Quickstart

### Install required packages
```bash
bash requirements.sh
```

### Set LLM API Key
```bash
export AZURE_API_KEY=your_azure_api_key
export AZURE_ENDPOINT=your_azure_endpoint
export OPENAI_API_KEY=your_openai_api_key
export GEMINI_API_KEY=your_genmini_api_key
```

### Run the benchmark
```bash
python run.py
```
Arguments:
- `--max_steps`: Maximum number of steps (default is 20)
- `--max_memory_length`: Maximum length of memory to retain (default is 15)
- `--suffix`: Suffix for the filename (default is an empty string)
- `--model`: Model to use for the benchmark (default is "gpt-4")
- `--temperature`: Sampling temperature (default is 0.0)
- `--top_p`: Top p sampling parameter (default is 0.9)
- `--max_tokens`: Maximum number of tokens per generation (default is 1500)
- `--stop_token`: Token that triggers stop in generation (default is None)
- `--test_all_meta_path`: Path to the meta configuration file (default is "da_code/configs/examples.jsonl")
- `--example_index`: Index range of the examples to run (default is "all")
- `--example_name`: Name of the example to run (default is an empty string)
- `--overwriting`: Enables overwriting existing files (default is False)
- `--retry_failed`: Retry failed evaluations (default is False)
- `--output_dir`: Directory for output files (default is "output")


### Evaluate the benchmark
```bash
python evaluate.py \
    --output_dir output/gpt4 \
    --gold_dir da_code/gold \
    --eval_json da_code/configs/eval_examples.jsonl \
    --result_file results/gpt4.json \
    --timeout_seconds 300
```

Arguments:
- `--output_dir`: Directory for output files
- `--gold_dir`: Directory for gold files
- `--eval_json`: Path to the evaluation configuration file 
- `--result_file`: Path to the result file
- `--timeout_seconds`: Timeout in seconds for each evaluation

### Get Full Dataset
We provide 100 examples of the dataset in the source folder. To get the full dataset, follow the instructions below:
* Download the source data from [here]()
* Unzip the dataset to da_code/source
```bash
unzip source.zip -d da_code/source
```
* Download the gold data from [here]()
* Unzip the gold data to da_code/gold
```bash
unzip gold.zip -d da_code/gold
```





