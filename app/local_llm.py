from __future__ import annotations
import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

try:
    from peft import PeftModel
except Exception:
    PeftModel = None


class LocalQwenLLM:
    """
    本地 Qwen 推理封装。

    默认读取环境变量：
    - QWEN_MODEL_PATH：基座模型路径
    - QWEN_ADAPTER_PATH：可选，LoRA adapter 路径
    """

    def __init__(self, model_path: str | None = None, adapter_path: str | None = None):
        self.model_path = model_path or os.getenv("QWEN_MODEL_PATH", "/home/host/ljy/model/model")
        self.adapter_path = adapter_path or os.getenv("QWEN_ADAPTER_PATH", "")

        print(f"加载 tokenizer: {self.model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True,
        )

        print(f"加载模型: {self.model_path}")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                dtype="auto",
                device_map="auto",
                trust_remote_code=True,
            )
        except TypeError:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype="auto",
                device_map="auto",
                trust_remote_code=True,
            )

        if self.adapter_path:
            if PeftModel is None:
                raise RuntimeError("检测到 QWEN_ADAPTER_PATH，但当前环境没有安装 peft。请先 pip install peft")
            print(f"加载 LoRA adapter: {self.adapter_path}")
            self.model = PeftModel.from_pretrained(self.model, self.adapter_path)

        self.model.eval()

        print("[LocalQwenLLM] model_load_done", flush=True)
        print("[LocalQwenLLM] model_device:", getattr(self.model, "device", None), flush=True)
        print("[LocalQwenLLM] hf_device_map:", getattr(self.model, "hf_device_map", None), flush=True)

        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        # 清理模型自带 generation_config 中的采样参数，避免 do_sample=False 时反复出现 warning。
        # 不影响生成结果，只是让评测日志更干净。
        self.model.generation_config.do_sample = False
        self.model.generation_config.temperature = None
        self.model.generation_config.top_p = None
        self.model.generation_config.top_k = None

    def chat(self, messages, max_new_tokens: int = 180) -> str:
        env_max_new_tokens = os.getenv("LOCAL_LLM_MAX_NEW_TOKENS")
        if env_max_new_tokens:
            max_new_tokens = int(env_max_new_tokens)

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        ).to(self.model.device)

        print(
            f"[LocalQwenLLM] generate_start input_tokens={inputs['input_ids'].shape[-1]} max_new_tokens={max_new_tokens} device={self.model.device}",
            flush=True,
        )
        t0 = time.time()

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                use_cache=True,
                repetition_penalty=1.05,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        print(
            f"[LocalQwenLLM] generate_done cost={time.time() - t0:.2f}s output_tokens={outputs.shape[-1]}",
            flush=True,
        )

        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        ).strip()

        return response
