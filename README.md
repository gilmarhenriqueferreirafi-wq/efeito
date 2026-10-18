# Efeito Holográfico

Script em Python que transforma uma imagem em padrões de interferência com aparência holográfica. O projeto usa transformadas de Fourier e franjas de Gabor.

## Saídas geradas

Ao executar o `holo.py`, três arquivos são criados na pasta `holo_out`:

- `rainbow_<nome>.png`: composição colorida com interferência e separação de cores, criando um efeito holográfico com tons de vermelho, verde e azul.
- `gabor_<nome>.png`: padrão monocromático formado por franjas diagonais de Gabor. O contraste das linhas carrega a informação visual da imagem.
- `gabor_anaglifo_<nome>.png`: versão vermelho/ciano com deslocamento entre os canais, preparada para produzir sensação de profundidade com óculos 3D.

A imagem usada nos testes locais foi uma captura do Android Studio. Ela serve apenas como entrada de exemplo e não faz parte do repositório.

## Instalação

```powershell
py -m pip install numpy Pillow
```

## Uso

```powershell
py holo.py "C:\caminho\para\imagem.png"
```

Também é possível ajustar o tamanho, o período das franjas e a pasta de saída:

```powershell
py holo.py imagem.png --size 1200 --period 9 --out-dir holo_out
```

## Observações

O resultado é uma simulação digital de interferência e difração. A aparência do efeito depende da imagem de entrada, do tamanho e dos parâmetros escolhidos.
