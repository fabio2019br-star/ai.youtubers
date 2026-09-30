#!/usr/bin/env python3
"""
cross_viral.py — Motor de Viralização Cruzada TikTok ↔ Reels

Copyright (c) 2026 [SEU NOME OU ORGANIZAÇÃO]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Uso: baixa um vídeo de qualquer uma das plataformas, gera DUAS versões
com "impressões digitais" (fingerprints) diferentes, cada uma adaptada
às características nativas do TikTok ou do Reels.

Não publica automaticamente — apenas gera os arquivos prontos para upload.
"""

import os
import subprocess
import tempfile
import hashlib
import random
import json
from pathlib import Path
from dataclasses import dataclass


# ─────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────

@dataclass
class PlatformProfile:
    """Parâmetros nativos de cada plataforma"""
    name: str
    target_width: int
    target_height: int
    crf: int              # Fator de qualidade (menor = melhor; 18-23 é a zona ideal)
    audio_bitrate: str    # "128k" / "192k"
    speed_factor: float   # Ajuste fino de velocidade — altera a fingerprint de áudio
    zoom_factor: float    # Zoom leve — altera a fingerprint visual


TIKTOK_PROFILE = PlatformProfile(
    name="tiktok",
    target_width=1080,
    target_height=1920,
    crf=20,
    audio_bitrate="128k",
    speed_factor=1.02,    # Aceleração leve, imperceptível ao olho humano
    zoom_factor=1.02,
)

REELS_PROFILE = PlatformProfile(
    name="reels",
    target_width=1080,
    target_height=1920,
    crf=21,
    audio_bitrate="192k",
    speed_factor=0.98,    # Desaceleração leve
    zoom_factor=1.03,
)


# ─────────────────────────────────────────────
# Motor principal
# ─────────────────────────────────────────────

class CrossViralEngine:
    def __init__(self, workdir: str = "cross_viral_work"):
        self.workdir = Path(workdir)
        self.workdir.mkdir(exist_ok=True)
        self.raw_dir = self.workdir / "raw"
        self.raw_dir.mkdir(exist_ok=True)

    # ---------- Passo 1: baixar o vídeo de origem ----------
    def download(self, url: str, out_name: str) -> Path:
        """
        Baixa com yt-dlp. Links do TikTok saem sem marca d'água
        (comportamento padrão do yt-dlp). Links do Reels também são suportados.
        """
        out_path = self.raw_dir / f"{out_name}.mp4"
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "--merge-output-format", "mp4",
            "-o", str(out_path),
            url,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return out_path

    # ---------- Passo 2: reescrever a fingerprint ----------
    def repurpose(self, src: Path, profile: PlatformProfile) -> Path:
        """
        Uma única codificação resolve três coisas:
        1. Zoom leve + ajuste de velocidade → muda a fingerprint visual e de áudio
        2. Recodificação → sobrescreve a assinatura original do codec
        3. Normalização de resolução → adapta à plataforma de destino

        Não inclui marca d'água de nenhuma plataforma — saída limpa.
        """
        out_path = self.workdir / f"{src.stem}_{profile.name}.mp4"

        # Monta a cadeia de filtros: escala → crop leve (zoom centralizado)
        # O zoom_factor é implementado via crop: amplia um pouco e recorta de volta
        zoom = profile.zoom_factor
        w, h = profile.target_width, profile.target_height

        # Amplia e depois recorta = zoom leve
        crop_w = int(w / zoom) if zoom > 1 else w
        crop_h = int(h / zoom) if zoom > 1 else h

        vf = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
            f"crop={crop_w}:{crop_h},"
            f"scale={w}:{h}"
        )

        # Ajuste de velocidade do áudio: usa atempo pra manter o tom,
        # mudando apenas a fingerprint temporal
        af = f"atempo={profile.speed_factor}"

        # Ajuste de velocidade do vídeo (sincronizado com o áudio)
        # O fator PTS = 1 / velocidade
        pts_factor = 1.0 / profile.speed_factor

        cmd = [
            "ffmpeg",
            "-i", str(src),
            "-vf", f"setpts={pts_factor}*PTS,{vf}",
            "-af", af,
            "-c:v", "libx264",
            "-crf", str(profile.crf),
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", profile.audio_bitrate,
            "-movflags", "+faststart",
            "-y",
            str(out_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return out_path

    # ---------- Passo 3: gerar pacote de legendas por plataforma ----------
    def generate_captions(self, base_caption: str, hashtags: list) -> dict:
        """
        Gera legendas com estilos diferentes pra cada plataforma.
        Observação: isto é só um template. No uso real, ajuste manualmente
        ou conecte a um LLM.
        """
        common_tags = hashtags[:3]

        return {
            "tiktok": {
                "caption": base_caption.lower().replace(".", ""),
                "hashtags": common_tags + random.sample(
                    ["fyp", "viral", "paravoce", "tiktokbrasil"], 2
                ),
                "note": "TikTok prefere minúsculas, frases curtas, 3-5 hashtags",
            },
            "reels": {
                "caption": base_caption,
                "hashtags": hashtags[:8],
                "note": "Reels prefere frases completas, emoji, 5-10 hashtags",
            },
        }

    # ---------- Fluxo principal ----------
    def process(self, url: str, name: str, base_caption: str, hashtags: list):
        """
        Fluxo completo:
        1. Baixa o vídeo de origem
        2. Gera a variante de fingerprint pro TikTok
        3. Gera a variante de fingerprint pro Reels
        4. Exporta o pacote de legendas
        """
        print(f"[1/4] Baixando vídeo de origem: {url}")
        raw = self.download(url, name)

        print(f"[2/4] Reescrevendo fingerprint pro TikTok...")
        tiktok_file = self.repurpose(raw, TIKTOK_PROFILE)

        print(f"[3/4] Reescrevendo fingerprint pro Reels...")
        reels_file = self.repurpose(raw, REELS_PROFILE)

        print(f"[4/4] Gerando pacote de legendas...")
        captions = self.generate_captions(base_caption, hashtags)

        manifest = {
            "source": str(raw),
            "outputs": {
                "tiktok": {
                    "file": str(tiktok_file),
                    "caption": captions["tiktok"]["caption"],
                    "hashtags": captions["tiktok"]["hashtags"],
                },
                "reels": {
                    "file": str(reels_file),
                    "caption": captions["reels"]["caption"],
                    "hashtags": captions["reels"]["hashtags"],
                },
            },
        }

        manifest_path = self.workdir / f"{name}_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

        print(f"\nConcluído. Arquivos em: {self.workdir}")
        print(f"Manifesto: {manifest_path}")
        return manifest


# ─────────────────────────────────────────────
# Exemplo de uso
# ─────────────────────────────────────────────

if __name__ == "__main__":
    engine = CrossViralEngine()

    # Exemplo: baixar do TikTok e gerar variante pro Reels
    engine.process(
        url="https://www.tiktok.com/@usuario/video/1234567890",
        name="meu_video",
        base_caption="Esse truque mudou tudo. Testa e me conta.",
        hashtags=["dicas", "viral", "tutorial", "aprender"],
    )