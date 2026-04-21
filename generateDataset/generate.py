import os
import csv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.8, 
    api_key=os.getenv("OPENAI_API_KEY") 
)

intent_dict = {
    "accusing": "Menuduh pemain lain secara langsung bahwa mereka adalah Gangster atau Ketua Gangster.",
    "defending": "Membela diri dari tuduhan, mengklaim diri sebagai netral yang miskin atau tidak bersalah.",
    "bluffing": "Berbohong atau menggertak, misalnya pura-pura jadi Polisi, pura-pura punya Shield, atau pura-pura miskin.",
    "probing": "Memancing informasi, menyelidiki siapa yang dirampok semalam, atau mencari tahu siapa yang memegang Invitation Card.",
    "neutral": "Obrolan basa-basi, mengeluh tentang nasib, atau menyuruh orang lain cepat mengambil turn.",
    "deflecting": "Mengkambinghitamkan (scapegoating) atau melempar tuduhan ke pemain lain saat posisinya sedang diserang/dituduh.",
    "persuading": "Menghasut, mengajak aliansi, atau memengaruhi warga untuk sepakat melakukan voting ke target tertentu.",
    "claiming": "Mendeklarasikan secara terbuka role atau Action Card yang dimiliki (bisa jujur atau bohong)."
}

prompt_template = PromptTemplate(
    input_variables=["intent_name", "intent_desc"],
    template="""Kamu adalah pembuat dataset bahasa Indonesia. Buat 50 variasi kalimat chat pendek bergaya bahasa seperti gamer Indonesia (kasual, slang, pakai kata seperti 'gw', 'lu', 'anjir', 'cuy', 'sus', 'fix', 'aku', 'kamu', 'dia', 'kita', 'kami, mereka'), dan gaya bahasa indonesia lainnya baik formal atau pun bahasa percakapan sehari- hari, baik kalangan anak anak hingga dewasa. 

Tema percakapannya adalah game strategi bernama "Shadow Heist". Berikut adalah aturan gamenya:
- Role awal: Netral (Petani, Pegawai, Penjual) dan 1 Polisi.
- Ada kartu Action: 'Shield' (kebal dirampok 1x), 'Toto' (dapat uang), 'Secret Card' (intip role/uang orang), 'Fake News' (menyebar rumor palsu), dan 'Invitation Card'.
- Siapapun yang dapat 'Invitation Card' berubah jadi role rahasia: Gangster atau Ketua Gangster.
- Gangster bisa merampok kekayaan orang. Hasil: 30% gangster biasa, 70% Ketua. 
- Polisi harus menebak target rampokan. Orang kaya bisa membayar Polisi untuk menjaganya.
- Jika Polisi menebak benar, Gangster di-freeze 3 turn dan hartanya disita Polisi.

TUGASMU:
Hasilkan kalimat untuk intent (niat percakapan): {intent_name}
Deskripsi intent: {intent_desc}

Format output WAJIB HANYA berupa baris teks CSV tanpa header, tanpa nomor urut, tanpa tanda kutip, dengan format:
kalimat_chat,{intent_name}

Contoh output yang benar:
pak polisi jagain gw dong ntar gw bayar pake duit toto,{intent_name}
shield gw aktif ya berani nyerang gw auto beku lu 3 turn,{intent_name}
"""
)

def generate_dataset():
    print("Mulai men-generate dataset sintetis menggunakan GPT-4o...\n")
    
    os.makedirs("data", exist_ok=True)
    dataset_path = "data/chat_dataset.csv"
    
    with open(dataset_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["teks_chat", "label_intent"]) 
        
        for intent_name, intent_desc in intent_dict.items():
            print(f"Memproses kelas: [{intent_name}]...")
            
            for i in range(2): 
                print(f"  > Iterasi ke-{i+1} untuk {intent_name}...")
                prompt = prompt_template.format(intent_name=intent_name, intent_desc=intent_desc)
                
                try:
                    response = llm.invoke(prompt)
                    output_text = response.content.strip()
                    
                    lines = output_text.split('\n')
                    for line in lines:
                        if line.strip(): 
                            parts = line.rsplit(',', 1)
                            if len(parts) == 2:
                                writer.writerow([parts[0].strip(), parts[1].strip()])
                    
                except Exception as e:
                    print(f" [X] Error saat memproses {intent_name} iterasi {i+1}: {e}\n")
            print(f"Selesai mengumpulkan data untuk {intent_name}!\n")

    print(f"Selesai! Dataset berhasil disimpan di: {dataset_path}")

if __name__ == "__main__":
    generate_dataset()