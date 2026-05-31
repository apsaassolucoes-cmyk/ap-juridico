import os
import requests
from datetime import datetime, timedelta, date

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
EMAILJS_SERVICE_ID = os.environ.get("EMAILJS_SERVICE_ID")
EMAILJS_TEMPLATE_ID = os.environ.get("EMAILJS_TEMPLATE_ID")
EMAILJS_USER_ID = os.environ.get("EMAILJS_USER_ID")
EMAIL_DESTINO = "adrianosilva3030@gmail.com"

def buscar_prazos():
    limite = (date.today() + timedelta(days=7)).isoformat()
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/ap_prazos?status=eq.pendente&data_vencimento=lte.{limite}&select=*"
    r = requests.get(url, headers=headers)
    return r.json()

def enviar_email(prazos):
    if not prazos:
        print("Nenhum prazo encontrado.")
        return
    hoje = date.today().isoformat()
    urgentes = [p for p in prazos if p['data_vencimento'] <= hoje]
    proximos = [p for p in prazos if p['data_vencimento'] > hoje]
    corpo = f"AP Soluções Jurídicas — Relatório Diário\nData: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n"
    if urgentes:
        corpo += f"🔴 URGENTES: {len(urgentes)}\n"
        for p in urgentes:
            corpo += f"• {p['titulo']} — {p['data_vencimento']} — {p['prioridade']}\n"
    corpo += f"\n📅 PRÓXIMOS 7 DIAS: {len(proximos)}\n"
    for p in proximos:
        corpo += f"• {p['titulo']} — {p['data_vencimento']} — {p['prioridade']}\n"
    corpo += "\n— AP Sistema | OAB/PI nº 13.896"
    assunto = f"[AP Alertas] {'🔴 URGENTE — ' if urgentes else ''}Prazos {datetime.now().strftime('%d/%m/%Y')}"
    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_USER_ID,
        "template_params": {"subject": assunto, "message": corpo, "name": "AP Sistema", "email": EMAIL_DESTINO, "to_email": EMAIL_DESTINO}
    }
    r = requests.post("https://api.emailjs.com/api/v1.0/email/send", json=payload)
    print(f"E-mail enviado!" if r.status_code == 200 else f"Erro: {r.text}")

if __name__ == "__main__":
    print(f"Verificando — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    prazos = buscar_prazos()
    print(f"Encontrados: {len(prazos)}")
    enviar_email(prazos)
    print("Concluído!")
