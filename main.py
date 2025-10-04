import os
import time
import pandas as pd
from lojas import kabum, amazon, mercadolivre, gkinfostore, pichau
from telegram.enviar_alerta import enviar_alerta

# Carrega configurações
def carregar_config():
    with open("config/lojas_ativas.txt") as f:
        lojas = [l.strip() for l in f if l.strip()]
    with open("config/palavras_chave.txt") as f:
        kws = []
        for line in f:
            parts = line.strip().split(";")
            kws.append({
                "produto": parts[0],
                "preco_max": float(parts[1]) if parts[1] else None,
                "loja": parts[2] if len(parts)>2 and parts[2] else None
            })
    filtros = pd.read_json("config/filtros_preco.json", typ="series").to_dict()
    return lojas, kws, filtros

def salvar_preco(data):
    df = pd.DataFrame(data)
    file = "historico/precos.csv"
    if os.path.exists(file):
        df_old = pd.read_csv(file)
        df = pd.concat([df_old, df], ignore_index=True)
    df.to_csv(file, index=False)
    return df

def gerar_graficos(df):
    import matplotlib.pyplot as plt
    for produto in df['produto'].unique():
        sub = df[df['produto']==produto]
        plt.figure()
        plt.plot(pd.to_datetime(sub['timestamp']), sub['preco'], marker='o')
        plt.title(produto)
        plt.xlabel("Data")
        plt.ylabel("Preço (R$)")
        plt.grid(True)
        plt.savefig(f"historico/graficos/{produto.replace(' ','_')}.png")
        plt.close()

def main():
    lojas_ativas, kws, filtros = carregar_config()
    resultados = []
    for kw in kws:
        for nome, modulo in [("kabum", kabum), ("amazon", amazon),
                             ("mercadolivre", mercadolivre),
                             ("gkinfostore", gkinfostore),
                             ("pichau", pichau)]:
            if nome not in lojas_ativas:
                continue
            if kw['loja'] and kw['loja'] != nome:
                continue
            encontrados = modulo.buscar(kw['produto'])
            for prod in encontrados:
                prod['produto'] = kw['produto']
                prod['loja'] = nome
                prod['timestamp'] = pd.Timestamp.now()
                resultados.append(prod)
                preco_ok = True
                if kw['preco_max']:
                    preco_ok = prod['preco'] <= kw['preco_max']
                if filtros.get(nome) and prod['preco'] > filtros[nome]:
                    preco_ok = False
                if preco_ok:
                    link = prod['link']
                    enviar_alerta(prod['titulo'], prod['preco'], nome, link)
    if resultados:
        df = salvar_preco(resultados)
        gerar_graficos(df)

if __name__ == "__main__":
    main()
