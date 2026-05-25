import gradio as gr
import requests
import plotly.graph_objects as go

def analyze_github_profile(username):
    if not username:
        return "Kullanıcı adı girin!", None, ""
    
    # Kullanıcı bilgilerini çek
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    
    user_res = requests.get(user_url)
    repos_res = requests.get(repos_url)
    
    if user_res.status_code != 200:
        return "Kullanıcı bulunamadı!", None, ""
    
    user = user_res.json()
    repos = repos_res.json()
    
    # Dil istatistikleri
    languages = {}
    stars = 0
    for repo in repos:
        if repo.get("language"):
            lang = repo["language"]
            languages[lang] = languages.get(lang, 0) + 1
        stars += repo.get("stargazers_count", 0)
    
    # Geliştirici tipi tahmini
    ai_langs = {"Python", "Jupyter Notebook"}
    backend_langs = {"Java", "Go", "Ruby", "PHP", "C#"}
    frontend_langs = {"JavaScript", "TypeScript", "HTML", "CSS"}
    
    lang_set = set(languages.keys())
    if lang_set & ai_langs:
        dev_type = "🤖 AI / Data Science Geliştirici"
    elif lang_set & backend_langs:
        dev_type = "⚙️ Backend Geliştirici"
    elif lang_set & frontend_langs:
        dev_type = "🎨 Frontend Geliştirici"
    else:
        dev_type = "💻 Full Stack Geliştirici"
    
    # Skor hesapla
    score = min(100, (
        (user.get("public_repos", 0) * 2) +
        (user.get("followers", 0) * 3) +
        (stars * 5)
    ))
    
    # Analiz metni
    analysis = f"""
## 👤 {user.get('name', username)}

**Geliştirici Tipi:** {dev_type}
**Profil Skoru:** {score}/100
**Toplam Repo:** {user.get('public_repos', 0)}
**Takipçi:** {user.get('followers', 0)}
**Toplam Yıldız:** {stars}
**Konum:** {user.get('location', 'Belirtilmemiş')}

### 💡 Öneriler
{"✅ Harika bir profil!" if score > 50 else "📌 Daha fazla proje ekle ve README yaz!"}
{"✅ Aktif geliştirici!" if user.get('public_repos', 0) > 10 else "📌 Repo sayını artır!"}
{"✅ İyi takipçi kitlesi!" if user.get('followers', 0) > 20 else "📌 Topluluğa katıl, takipçi kazan!"}
    """
    
    # Grafik
    if languages:
        fig = go.Figure(go.Pie(
            labels=list(languages.keys()),
            values=list(languages.values()),
            hole=0.4
        ))
        fig.update_layout(title="Programlama Dili Dağılımı")
    else:
        fig = None
    
    return analysis, fig, f"Profil Skoru: {score}/100"

with gr.Blocks(title="GitHub Profil Analyzer") as demo:
    gr.Markdown("# 🔍 GitHub Profil Analyzer")
    gr.Markdown("GitHub kullanıcı adını gir, profilini analiz edelim!")
    
    with gr.Row():
        username_input = gr.Textbox(placeholder="örn: torvalds", label="GitHub Kullanıcı Adı")
        analyze_btn = gr.Button("Analiz Et 🚀", variant="primary")
    
    with gr.Row():
        analysis_output = gr.Markdown()
        chart_output = gr.Plot()
    
    score_output = gr.Textbox(label="Skor")
    
    analyze_btn.click(
        fn=analyze_github_profile,
        inputs=username_input,
        outputs=[analysis_output, chart_output, score_output]
    )

demo.launch()