from typing import Any, Dict

import threading

from helm.common.cache import CacheConfig
from helm.common.optional_dependencies import handle_module_not_found_error
from helm.tokenizers.caching_tokenizer import CachingTokenizer
from transformers import PreTrainedTokenizerBase, PreTrainedTokenizerFast

try:
    import anthropic
except ModuleNotFoundError as e:
    handle_module_not_found_error(e, ["anthropic"])


class AnthropicTokenizer(CachingTokenizer):
    LOCK: threading.Lock = threading.Lock()
    """Global lock for the Anthropic tokenizer.

    The Anthropic tokenizer is a wrapper around a single global Hugging Face tokenizer, which is thread-hostile."""

    def __init__(self, cache_config: CacheConfig) -> None:
        super().__init__(cache_config)
        with AnthropicTokenizer.LOCK:
            self._tokenizer: PreTrainedTokenizerBase = PreTrainedTokenizerFast(
                tokenizer_object=anthropic.Anthropic().get_tokenizer()
            )

    def _tokenize_do_it(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if request["encode"]:
            if request["truncation"]:
                with AnthropicTokenizer.LOCK:
                    tokens = self._tokenizer.encode(
                        request["text"],
                        truncation=request["truncation"],
                        max_length=request["max_length"],
                        add_special_tokens=False,
                    )
            else:
                with AnthropicTokenizer.LOCK:
                    tokens = self._tokenizer.encode(request["text"], add_special_tokens=False)
        else:
            # No encoding, just return the token strings
            tokens = [self._tokenizer.convert_tokens_to_string([i]) for i in self._tokenizer.tokenize(request["text"])]
        return {"tokens": tokens}

    def _decode_do_it(self, request: Dict[str, Any]) -> Dict[str, Any]:
        with AnthropicTokenizer.LOCK:
            text = self._tokenizer.decode(
                request["tokens"], clean_up_tokenization_spaces=request["clean_up_tokenization_spaces"]
            )
        return {"text": text}
