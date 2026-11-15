# 🔄 Git Repo Exchanges

GitHub repository'larini bir akkauntdan boshqasiga ko'chirish (klonlash) uchun skript namunasi.

---

## ✨ Imkoniyatlar

- 📋 **Repo ro'yxatini olish:** GitHub API orqali
- 📥 **Ommaviy klonlash:** barcha repolarni lokal saqlash
- 🔑 **Token bilan autentifikatsiya**

---

## 🛠 Texnologiyalar

| Texnologiya | Maqsad |
|---|---|
| **Python 3.10+** | Asosiy til |
| **requests** | GitHub API |

---

## ⚙️ O'rnatish va sozlash

```bash
git clone https://github.com/dastonbek8747/git_repo_exchanges.git
cd git_repo_exchanges
pip install requests
```

`main.py` faylida o'z ma'lumotlaringizni to'ldiring (fayl hozircha izoh holida — namunadir):

```python
old_username = "eski_username"
old_token = "api_token"
base_path = "/path/to/save/"
```

---

## ▶️ Ishga tushirish

```bash
python main.py
```

> 🔒 Tokenni kodga yozib qoldirmang — muhit o'zgaruvchisidan foydalaning.

---

## 📁 Loyiha tuzilishi

```
git_repo_exchanges/
├── main.py            # Skript namunasi (izohlangan)
└── .idea/
```

---

## 📄 Litsenziya

Litsenziya ko'rsatilmagan.
