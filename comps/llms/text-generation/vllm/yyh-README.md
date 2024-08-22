#### launch vllm
```
docker run --rm --runtime nvidia --gpus all     -v /mnt/opea-models:/root/.cache/huggingface/hub     --env "HUGGING_FACE_HUB_TOKEN=$HF_token"     -p 8000:8000     --ipc=host     vllm/vllm-openai:latest     --model Intel/neural-chat-7b-v3-3
```

#### microservice
##### build
```
cd ../../../../
docker build  -t opea/llm-vllm-yyh:latest \
    --build-arg https_proxy=$https_proxy \
    --build-arg http_proxy=$http_proxy \
    -f comps/llms/text-generation/vllm/docker/Dockerfile.microservice-yyh .
```

##### launch
```
docker run -it --rm     --name="llm-vllm-server"     -p 9000:9000     --ipc=host     -e http_proxy=$http_proxy     -e https_proxy=$https_proxy -e no_proxy=$no_proxy    -e vLLM_ENDPOINT=http://localhost:8000     -e HUGGINGFACEHUB_API_TOKEN=$HF_token     -e LLM_MODEL=Intel/neural-chat-7b-v3-3     -e LOGFLAG=$LOGFLAG     opea/llm-vllm-yyh:latest
```



#### test
```
curl -x "" http://127.0.0.1:9000/v1/chat/completions     -H "Content-Type: application/json"     -d '{
        "model": "Intel/neural-chat-7b-v3-3",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]}'
```