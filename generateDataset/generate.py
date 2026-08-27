import os
import csv
from time import sleep
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.6-luna",
    temperature=0.8,
    reasoning_effort="medium",
    api_key=os.getenv("OPENAI_API_KEY")
)

intent_dict = {
    "accusing": "Menuduh pemain lain sebagai Hitman berdasarkan observasi chat atau kejadian Gag Order.",
    "defending": "Membela diri dari tuduhan pemain lain, baik merespons secara santai maupun tegas.",
    "bluffing": "Berbohong mengenai peran yang dimiliki, misalnya Hitman yang berpura-pura menjadi Stalker atau Spy.",
    "probing": "Memancing dan menggali informasi rahasia, seperti bertanya siapa yang dijaga Spy tadi malam.",
    "deflecting": "Mengalihkan isu atau melempar balik tuduhan ke pemain lain saat posisinya sedang diserang.",
    "persuading": "Menghasut dan menggiring opini warga agar sepakat mengeksekusi pemain tertentu saat fase voting.",
    "claiming": "Mendeklarasikan peran atau identitas secara terbuka (bisa jujur atau bohong) untuk mendapatkan kepercayaan.",
    "neutral": "Obrolan basa-basi, reaksi kaget, atau sekadar merespons sistem tanpa ada niat taktis."
}

prompt_template = PromptTemplate(
    input_variables=["intent_name", "intent_desc"],
    template="""Kamu adalah pembuat dataset bahasa Indonesia. Buat 50 variasi kalimat chat pendek bergaya bahasa gamer Indonesia (kasual, slang, optional pakai kata seperti 'gw', 'lu', 'sus', 'fix', 'aku', 'kamu', 'dia', 'kita', 'kami', 'mereka'), dan gaya bahasa indonesia lainnya baik formal atau pun bahasa percakapan sehari-hari. 
    ingat buat percakapannya senatural mungkin 

Tema percakapannya adalah game social deduction murni bernama "Shadow Heist". Berikut adalah aturan gamenya:
- Zero Economy: Tidak ada uang, brankas, atau polisi. 
- Role: Hitman (Jahat), Spy (Pelindung), Stalker (Intel), Civilian (Warga biasa).
- Skill Hitman: Di fase malam menyandera (Hostage) 1 korban. Di fase siang punya skill 'Gag Order' (membungkam chat 1 orang mendadak untuk menebar fitnah).
- Skill Spy: Di fase malam mengawal/melindungi (Guard) 1 orang. Jika orang itu diserang Hitman, target selamat. Syarat: tidak bisa mengawal orang yang sama 2 malam berturut-turut.
- Skill Stalker: Di fase malam bisa mengintip (Peek) identitas asli 1 pemain (cooldown 1x tiap 2 ronde).
- Fase Siang (Diskusi): Semua berdebat di chat. Hitman bisa pakai Gag Order.
- Fase Malam (Aksi): Chat dikunci, semua role beraksi buta tanpa tahu target satu sama lain.
- Fase Tribunal (Pagi): Semua orang voting. Pemain dengan vote terbanyak langsung dieksekusi mati.

TUGASMU:
Hasilkan kalimat untuk intent (niat percakapan): {intent_name}
Deskripsi intent: {intent_desc}

Format output WAJIB HANYA berupa baris teks CSV tanpa header, tanpa nomor urut, tanpa tanda kutip, dengan format:
kalimat_chat,{intent_name}

Contoh output yang benar:
eh si A aneh banget dari tadi diem aja, fix dia hitmannya,{intent_name}
sumpah bukan aku hitmannya, gw civilian biasa,{intent_name}
gw stalker, semalem gw intip si B dia aman,{intent_name}

kasih output yang dataset friendly
"""

)

print("Model:", llm.model_name)
print("Temperature:", llm.temperature)
model = llm.model_name

def generate_dataset():
    print("Mulai men-generate dataset sintetis menggunakan " + model + "...\n")
    
    os.makedirs("data", exist_ok=True)
    dataset_path = "data/chat_dataset2.csv"
    
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
                    file.flush() 
                    
                    sleep(2)
                    
                except Exception as e:
                    print(f" [X] Error saat memproses {intent_name} iterasi {i+1}: {e}\n")
                    
            print(f"Selesai mengumpulkan data untuk {intent_name}!\n")

    print(f"Selesai! Dataset berhasil disimpan di: {dataset_path}")

if __name__ == "__main__":
    # print("Memulai proses generate dataset...")
    generate_dataset()