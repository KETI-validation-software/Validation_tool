import pandas as pd
import re
from collections import Counter

# 데이터 로드
df = pd.read_csv('ACCV_2024_Abstracts.csv')

# 카테고리별 키워드 정의
keywords = {
    "Practical": ["real-world", "efficient", "robust", "speed", "latency", "deployment", "on-device", "practical", "medical", "autonomous", "real-time"],
    "Theoretical": ["theoretical", "mathematical", "proof", "convergence", "topology", "geometry", "invariant", "framework", "analysis"],
    "New Design": ["novel architecture", "new paradigm", "propose a novel", "introduce a new", "first to", "redefining", "rethink"],
    "Improvement": ["improve", "enhance", "revisit", "extend", "refine", "boost", "adapter", "fine-tuning", "distillation"],
    "VLM": ["vlm", "vision-language", "foundation model", "multimodal", "clip", "blip", "captioning", "text-to-image"],
    "Lightweight": ["lightweight", "efficient", "fast", "mobile", "memory-efficient", "on-device", "pruning", "quantization"]
}

def analyze_trend(text, kw_list):
    text = str(text).lower()
    return 1 if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in kw_list) else 0

# 통계 계산
for cat, kws in keywords.items():
    df[cat] = df.apply(lambda x: analyze_trend(str(x['Title']) + " " + str(x['Abstract']), kws), axis=1)

print("--- ACCV 2024 통계 결과 ---")
print(df[list(keywords.keys())].mean() * 100)

# 기술 키워드 빈도 분석
all_text = " ".join(df['Title'] + " " + df['Abstract']).lower()
tech_list = ["3d", "diffusion", "mamba", "transformer", "nerf", "video", "tracking", "detection", "segmentation", "depth"]
tech_counts = {kw: len(re.findall(r'\b' + re.escape(kw) + r'\b', all_text)) for kw in tech_list}
print("\n--- 기술 키워드 빈도 ---")
print(dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)))