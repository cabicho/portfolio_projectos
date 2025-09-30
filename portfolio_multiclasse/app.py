import gradio as gr
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
import os

# Configuração da porta para Render
port = int(os.getenv("PORT", 10000))

def create_sample_data():
    """Cria dados de exemplo para classificação multiclasse"""
    X, y = make_classification(
        n_samples=1000,
        n_features=4,
        n_informative=2,
        n_redundant=0,
        n_repeated=0,
        n_classes=3,
        n_clusters_per_class=1,
        random_state=42
    )
    
    feature_names = [f"Feature_{i+1}" for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['Target'] = y
    df = df.round(3)
    
    return df

def predict_class(feature1, feature2, feature3, feature4):
    """Função de predição simulada"""
    # Simulação de um modelo de machine learning
    np.random.seed(hash(f"{feature1}{feature2}{feature3}{feature4}") % 10000)
    prediction = np.random.randint(0, 3)
    probabilities = np.random.dirichlet(np.ones(3), size=1)[0]
    
    classes = ['Classe A', 'Classe B', 'Classe C']
    
    result = {
        "Predição": classes[prediction],
        "Confiança": f"{probabilities[prediction]:.2%}",
        "Detalhes das Probabilidades": {
            classes[i]: f"{prob:.3f}" for i, prob in enumerate(probabilities)
        }
    }
    
    return result

def show_data_sample(n_samples=10):
    """Mostra uma amostra dos dados"""
    df = create_sample_data()
    return df.head(n_samples)

def generate_stats():
    """Gera estatísticas dos dados"""
    df = create_sample_data()
    stats = {
        "Estatísticas Gerais": {
            "Total de Amostras": len(df),
            "Número de Features": 4,
            "Número de Classes": 3,
            "Classes": ["A", "B", "C"]
        },
        "Estatísticas Descritivas": df.describe().round(3).to_dict()
    }
    correlation = df.corr().round(3)
    return stats, correlation

# Criar a interface Gradio
with gr.Blocks(
    title="Dashboard Multiclasse - Docker no Render",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    """
) as demo:
    
    gr.Markdown(
        """
        # 🎯 Dashboard de Classificação Multiclasse
        ## 🐋 **Deploy com Dockerfile no Render**
        
        *Sistema de demonstração para classificação multiclasse usando Gradio*
        """
    )
    
    with gr.Tab("🎯 Predição Interativa"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🔧 Configure as Features:")
                with gr.Row():
                    feature1 = gr.Slider(-4, 4, value=0.5, label="Feature 1", step=0.1)
                    feature2 = gr.Slider(-4, 4, value=-0.2, label="Feature 2", step=0.1)
                with gr.Row():
                    feature3 = gr.Slider(-4, 4, value=1.2, label="Feature 3", step=0.1)
                    feature4 = gr.Slider(-4, 4, value=-1.0, label="Feature 4", step=0.1)
                
                predict_btn = gr.Button("🔮 Executar Predição", variant="primary", size="lg")
            
            with gr.Column():
                gr.Markdown("### 📊 Resultado da Predição:")
                output = gr.JSON(label="Detalhes da Predição")
                
                gr.Markdown("### 📈 Informações Técnicas:")
                gr.Markdown("""
                - **Modelo**: Simulação de Classificação Multiclasse
                - **Classes**: A, B, C
                - **Features**: 4 características numéricas
                - **Deploy**: Docker no Render
                """)
        
        predict_btn.click(
            fn=predict_class,
            inputs=[feature1, feature2, feature3, feature4],
            outputs=output
        )
    
    with gr.Tab("📁 Dados e Amostras"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📋 Controle de Amostras:")
                data_count = gr.Slider(5, 50, value=10, label="Número de Amostras", step=5)
                data_btn = gr.Button("🔄 Carregar Dados", variant="secondary", size="lg")
            
            with gr.Column():
                gr.Markdown("### 📊 Visualização de Dados:")
                data_output = gr.Dataframe(
                    label="Amostra dos Dados Gerados",
                    headers=["Feature_1", "Feature_2", "Feature_3", "Feature_4", "Target"],
                    datatype=["number", "number", "number", "number", "number"],
                    row_count=5,
                    col_count=5,
                    wrap=True
                )
        
        data_btn.click(
            fn=lambda n: show_data_sample(int(n)),
            inputs=[data_count],
            outputs=data_output
        )
    
    with gr.Tab("📈 Análise Estatística"):
        gr.Markdown("### 📊 Estatísticas Descritivas")
        stats_btn = gr.Button("📋 Gerar Análise Estatística", variant="primary")
        
        with gr.Row():
            with gr.Column():
                stats_output = gr.JSON(label="Estatísticas dos Dados")
            with gr.Column():
                correlation_output = gr.Dataframe(
                    label="Matriz de Correlação",
                    headers=["F1", "F2", "F3", "F4", "Target"],
                    row_count=5,
                    col_count=5
                )
        
        stats_btn.click(
            fn=generate_stats,
            outputs=[stats_output, correlation_output]
        )
    
    with gr.Tab("🐋 Sobre o Deploy"):
        gr.Markdown(
            """
            ## 🚀 Configuração Docker no Render
            
            ### 📦 Estrutura do Projeto:
            ```
            portfolio_multiclasse_gradfo/
            ├── Dockerfile          # Configuração do container
            ├── requirements.txt    # Dependências Python
            ├── app.py             # Aplicação Gradio
            └── (sem render.yaml)   # Deploy manual
            ```
            
            ### 🔧 Tecnologias Utilizadas:
            - **Python 3.9** (runtime)
            - **Gradio 4.13.0** (interface web)
            - **Pandas & NumPy** (processamento de dados)
            - **Scikit-learn** (geração de dados)
            - **Docker** (containerização)
            
            ### 🌐 Configuração de Rede:
            - **Porta**: 10000 (configurável via variável PORT)
            - **Health Check**: Automático via curl
            - **Protocol**: HTTP
            
            ### ✅ Status do Deploy:
            - **Container**: 🐋 Dockerfile
            - **Platform**: Render.com
            - **Config**: Manual (sem render.yaml)
            - **Health**: ✅ Monitorado
            """
        )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        debug=False
    )