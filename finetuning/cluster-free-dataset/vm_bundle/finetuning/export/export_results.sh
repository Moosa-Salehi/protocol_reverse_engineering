cd /home/user01/finetuning

mkdir -p qwen25-coder-7b-protocol-re

rsync -a \
  output/qwen25-coder-7b-protocol-re/adapter/ \
  qwen25-coder-7b-protocol-re/adapter/

mkdir -p qwen25-coder-7b-protocol-re/gguf
cp \
  output/qwen25-coder-7b-protocol-re/gguf/qwen25-coder-7b-protocol-re-Q4_K_M.gguf \
  qwen25-coder-7b-protocol-re/gguf/

mkdir -p qwen25-coder-7b-protocol-re/test
cp \
  output/test/base.json \
  output/test/finetuned.json \
  output/test/comparison.json \
  qwen25-coder-7b-protocol-re/test/

cp \
  output/qwen25-coder-7b-protocol-re/config.json \
  output/qwen25-coder-7b-protocol-re/environment.json \
  qwen25-coder-7b-protocol-re/

tar -cf qwen25-coder-7b-protocol-re-artifacts.tar \
  qwen25-coder-7b-protocol-re/

