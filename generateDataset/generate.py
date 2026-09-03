import os
import csv
import random
from time import sleep
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.6-luna",
    temperature=0.9,
    reasoning_effort="high",
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

personas = [
    "Pemain analitis. Berfokus pada pengumpulan informasi, mengamati pola, dan memberikan argumen yang terstruktur dan objektif.",
    "Pemain pasif. Cenderung irit bicara, hanya merespons saat ditanya, dan mengikuti alur suara mayoritas saat mengambil keputusan.",
    "Pemain defensif. Sangat reaktif terhadap tuduhan, fokus utamanya adalah mematahkan argumen yang menyudutkan dirinya dan membersihkan namanya.",
    "Pemain inisiator. Proaktif mengambil alih alur diskusi, menyimpulkan situasi, dan mengarahkan target voting kepada pemain lain.",
    "Pemain pengamat lambat. Cenderung tertinggal alur diskusi, bermain berdasarkan informasi sepotong-sepotong, dan sering meminta pengulangan konteks.",
    "Pemain provokator. Gaya bermainnya berfokus pada memancing reaksi pemain lain lewat komentar yang menjebak untuk melihat respons mereka.",
    "Pemain adaptif. Bermain secara natural dan netral, menyesuaikan gaya komunikasinya dengan situasi saat itu tanpa pola tindakan yang terlalu menonjol.",
    "Pemain skeptis. Tidak mudah percaya pada opini mayoritas atau pemain yang terlalu mendominasi diskusi. Selalu mempertanyakan pernyataan orang lain.",
    "Pemain spekulatif. Sering melempar teori, asumsi, atau gertakan (bluffing) meski tanpa bukti kuat, demi melihat siapa yang setuju atau terpancing.",
    "Pemain kolaborator. Fokus mencari satu atau dua pemain lain untuk dipercaya sejak awal, membentuk aliansi tidak resmi, dan saling mendukung saat voting.",
    "Pemain teguh pendirian. Memiliki kecenderungan untuk mengunci satu target atau teori sejak awal (tunnel-vision), dan sangat sulit mengubah pendapat meski ada bukti baru.",
    "Pemain pelapor. Fokus menceritakan apa yang dia alami atau lakukan secara datar tanpa memberikan opini, analisis, atau tuduhan secara langsung."
]

prompt_template = PromptTemplate(
    input_variables=["intent_name", "intent_desc", "persona"],
    template="""Kamu adalah pembuat dataset bahasa Indonesia. Buat 30 variasi kalimat chat pendek bergaya bahasa gamer Indonesia (kasual, slang, optional pakai kata seperti 'gw', 'lu', 'sus', 'fix', 'aku', 'kamu', 'dia', 'kita', 'kami', 'mereka'), dan gaya bahasa indonesia lainnya baik formal atau pun bahasa percakapan sehari-hari. 
    ingat buat percakapannya senatural mungkin 
    
    gaya atau persona percakapan kali ini adalah: {persona}

Tema percakapannya adalah game social deduction murni bernama "HOSTAGE". Berikut adalah aturan gamenya:
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

Format output WAJIB HANYA berupa baris teks CSV tanpa header, tanpa nomor urut, tanpa tanda kutip, dengan format pemisah garis lurus (pipe):
kalimat_chat|{intent_name}

Contoh output yang benar:
eh si A aneh banget dari tadi diem aja, fix dia hitmannya|{intent_name}
sumpah bukan aku hitmannya, gw civilian biasa|{intent_name}
gw stalker, semalem gw intip si B dia aman|{intent_name}

kasih output yang dataset friendly
dan pastikan hasil datasetnya berkualitas dengan variasi yang tinggi, natural, dan realistis. Jangan sampai ada kalimat yang sama persis.
"""

)

print("Model:", llm.model_name)
print("Temperature:", llm.temperature)
model = llm.model_name

def generate_dataset():
    print("Mulai men-generate dataset sintetis menggunakan " + model + "...\n")
    
    os.makedirs("data", exist_ok=True)
    dataset_path = "data/chat_dataset2.csv"
    
    file_exists = os.path.isfile(dataset_path)
    
    with open(dataset_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["teks_chat", "label_intent"])
                    
        for intent_name, intent_desc in intent_dict.items():
            print(f"Memproses kelas: [{intent_name}]...")
                     
                        
            for idx, current_persona in enumerate(personas):
                nama_persona_log = current_persona.split('.')[0].strip()
                print(f"  > Iterasi ke-{idx+1} untuk {intent_name} ({nama_persona_log})...")
                prompt = prompt_template.format(intent_name=intent_name, intent_desc=intent_desc, persona=current_persona)
                
                try:
                    response = llm.invoke(prompt)
                    
                    # 1. Bersihkan markdown jika LLM ngeyel menambahkan blok kode
                    output_text = response.content.strip()
                    output_text = output_text.replace("```csv", "").replace("```text", "").replace("```", "").strip()
                    
                    lines = output_text.split('\n')
                    for line in lines:
                        if not line.strip():
                            continue
                            
                        # 2. Pisahkan berdasarkan simbol pipa (|)
                        parts = line.split('|')
                        
                        if len(parts) != 2:
                            continue
                        
                        chat, label = parts
                        
                        # 3. Validasi label
                        if label.strip() == intent_name:
                            writer.writerow([
                                chat.strip(),
                                label.strip()
                            ])
                                                                                                        
                    file.flush() 
                    sleep(2)
                    
                except Exception as e:
                    print(f" [X] Error saat memproses {intent_name} iterasi {idx+1}: {e}\n")
                    
            print(f"Selesai mengumpulkan data untuk {intent_name}!\n")

    print(f"Selesai! Dataset berhasil disimpan di: {dataset_path}")

generate_dataset()