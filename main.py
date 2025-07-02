# import os
# import requests
#
# # 🔑 Profil ma'lumotlari
# old_username = "username"
# old_token = "api_token"
#
# new_username = "new_username"
# new_token = "new_api_token"
#
# # 📁 Qayerga saqlaymiz?
# base_path = "/home/doston/Downloads/Repos/"  # <<== O'ZINGIZGA MOS PATH
#
#
# # 🔄 1. Repositorylar ro‘yxatini olish
# def get_old_repos():
#     url = f"https://api.github.com/users/{old_username}/repos"
#     headers = {"Authorization": f"token {old_token}"}
#     response = requests.get(url, headers=headers)
#     return response.json()
#
#
# # 🔧 2. Yangi profilingizda repo yaratish
# def create_new_repo(repo_name):
#     url = "https://api.github.com/user/repos"
#     headers = {
#         "Authorization": f"token {new_token}",
#         "Accept": "application/vnd.github.v3+json"
#     }
#     data = {
#         "name": repo_name,
#         "private": False
#     }
#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code == 201:
#         print(f"✅ Yaratildi: {repo_name}")
#     elif response.status_code == 422:
#         print(f"⚠️ Allaqachon mavjud: {repo_name}")
#     else:
#         print(f"❌ Repo yaratishda xatolik: {response.json()}")
#
#
# # 🔃 3. Reponi klon qilish va push qilish
# def migrate_repo(repo):
#     repo_name = repo["name"]
#     clone_url = repo["clone_url"]
#
#     repo_path = os.path.join(base_path, repo_name)
#
#     print(f"\n📦 Klon qilinmoqda: {repo_name}")
#     os.system(f"git clone {clone_url} {repo_path}")
#
#     os.chdir(repo_path)
#
#     # Yangi profilingizda repo ochish
#     create_new_repo(repo_name)
#
#     # Remote manzilni almashtirish
#     os.system("git remote remove origin")
#     os.system(f"git remote add origin https://{new_username}:{new_token}@github.com/{new_username}/{repo_name}.git")
#
#     # Push qilish
#     print(f"🚀 Push qilinmoqda: {repo_name}")
#     os.system("git push -u origin main || git push -u origin master")
#
#     os.chdir(base_path)
#
#
# # 🟢 Bosh menyu
# if __name__ == "__main__":
#     os.makedirs(base_path, exist_ok=True)
#     repos = get_old_repos()
#     for repo in repos:
#         migrate_repo(repo)


import os
import requests
import subprocess
import time
from git import Repo, exc

# 🔑 Profil ma'lumotlari
old_username = "username"
old_token = "api_token"

new_username = "new_username"
new_token = "new_api_token"

# 📁 Saqlash joyi
base_path = "/home/user/Downloads/Repos"
os.makedirs(base_path, exist_ok=True)

# ⏱️ Qayta urinishlar uchun sozlamalar
MAX_RETRIES = 3
RETRY_DELAY = 5  # sekund


# 🔄 Repositorylar ro'yxatini olish
def get_old_repos():
    url = f"https://api.github.com/users/{old_username}/repos?per_page=100"
    headers = {"Authorization": f"token {old_token}"}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Repozitoriyalarni olishda xatolik (urinish {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    raise Exception("Repozitoriyalarni olish imkonsiz")


# 🔧 Yangi repo yaratish
def create_new_repo(repo_name):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {new_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": False,
        "auto_init": False
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code == 201:
                print(f"✅ Yaratildi: {repo_name}")
                return True
            elif response.status_code == 422:
                print(f"⚠️ Allaqachon mavjud: {repo_name}")
                return True
            else:
                print(f"❌ Repo yaratishda xatolik (HTTP {response.status_code}): {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Repo yaratishda xatolik (urinish {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    return False


# 🧹 Git tarixini tozalash
def clean_repo(repo_path):
    try:
        # .gitignore faylini tekshirish va yaratish
        gitignore_path = os.path.join(repo_path, '.gitignore')
        sensitive_patterns = [
            "# Maxfiy fayllar\n",
            ".env\n", "*.key\n", "*.pem\n", "config.json\n",
            "credentials.json\n", "secrets.ini\n", "*.env*\n"
        ]

        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r+') as f:
                content = f.read()
                for pattern in sensitive_patterns:
                    if pattern not in content:
                        f.write(pattern)
        else:
            with open(gitignore_path, 'w') as f:
                f.writelines(sensitive_patterns)

        # Maxfiy fayllarni o'chirish
        sensitive_files = [
            '.env', 'config.json', 'credentials.json',
            'secrets.ini', '.env.local', '.env.production'
        ]

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file in sensitive_files or file.endswith('.key') or file.endswith('.pem'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"⚠️ O'chirildi: {file_path.replace(repo_path, '')}")
                    except Exception as e:
                        print(f"❌ Faylni o'chirishda xatolik: {file_path} - {str(e)}")

        return True
    except Exception as e:
        print(f"❌ Tarixni tozalashda xatolik: {str(e)}")
        return False


# 🔄 Reponi ko'chirish
def migrate_repo(repo):
    repo_name = repo["name"]
    repo_path = os.path.join(base_path, repo_name)

    print(f"\n📦 Ko'chirilmoqda: {repo_name}")

    # 1. Avvalgi papkani tozalash
    if os.path.exists(repo_path):
        try:
            subprocess.run(f"rm -rf {repo_path}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Eski papkani tozalashda xatolik: {str(e)}")
            return

    # 2. Repozitoriyani klon qilish
    clone_url = repo["clone_url"].replace('https://', f'https://{old_username}:{old_token}@')

    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔄 Klon qilinmoqda (urinish {attempt + 1}/{MAX_RETRIES})...")
            subprocess.run(
                f"git clone --depth 1 --quiet {clone_url} {repo_path}",
                shell=True,
                check=True,
                timeout=300
            )
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"❌ Klon qilishda xatolik (urinish {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                if os.path.exists(repo_path):
                    subprocess.run(f"rm -rf {repo_path}", shell=True, check=True)
            else:
                return

    # 3. Tarixni tozalash
    if not clean_repo(repo_path):
        print(f"❌ {repo_name} tarixini tozalab bo'lmadi")
        return

    # 4. Yangi repozitoriya yaratish
    if not create_new_repo(repo_name):
        return

    # 5. Remote manzilni o'zgartirish
    os.chdir(repo_path)

    try:
        subprocess.run("git remote remove origin", shell=True, check=True)
        subprocess.run(
            f"git remote add origin https://{new_username}:{new_token}@github.com/{new_username}/{repo_name}.git",
            shell=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Remote manzilni o'zgartirishda xatolik: {str(e)}")
        os.chdir(base_path)
        return

    # 6. Push qilish
    print(f"🚀 Push qilinmoqda: {repo_name}")

    # Branch nomini aniqlash
    try:
        branch = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip()

        if not branch:
            branches = subprocess.run(
                "git branch -a",
                shell=True,
                capture_output=True,
                text=True
            ).stdout

            if "origin/main" in branches:
                branch = "master"
            else:
                branch = "main"

            # Lokal branch yaratish
            subprocess.run(f"git checkout -b {branch}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Branch nomini aniqlashda xatolik: {str(e)}")
        os.chdir(base_path)
        return

    # Push qilish
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔄 Push qilinmoqda (urinish {attempt + 1}/{MAX_RETRIES})...")
            subprocess.run(
                f"git push -u origin {branch} --force",
                shell=True,
                check=True,
                timeout=300
            )
            print(f"✔️ Muvaffaqiyatli push qilindi: {repo_name}")
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"❌ Push qilishda xatolik (urinish {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ {repo_name} push qilinmadi")

    os.chdir(base_path)


# 🟢 Asosiy dastur
if __name__ == "__main__":
    try:
        print("🔍 Repozitoriyalarni olish...")
        repos = get_old_repos()
        print(f"✅ {len(repos)} ta repozitoriya topildi")

        for repo in repos:
            try:
                migrate_repo(repo)
            except Exception as e:
                print(f"❌ {repo['name']} ko'chirishda kutilmagan xatolik: {str(e)}")
                continue

        print("\n✅ Barcha repozitoriyalar ko'chirildi!")
    except KeyboardInterrupt:
        print("\n⏹️ Dastur to'xtatildi")
    except Exception as e:
        print(f"\n❌ Asosiy xatolik: {str(e)}")