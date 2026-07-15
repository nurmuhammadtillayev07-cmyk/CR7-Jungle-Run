# CR7 Jungle Run 🏃‍♂️⚽

Pygame asosida yaratilgan "endless runner" uslubidagi o'yin. Android uchun Pydroid 3'da ishlashga moslashtirilgan, lekin kompyuterda ham (Windows/Linux/Mac) ishlaydi.

## Xususiyatlari

- Sakrash va egilish orqali to'siqlardan qochish
- Tangalar, futbol to'plari va bonuslar (qalqon, tezlik) yig'ish
- Kun/tun sikli, yomg'ir effekti, parallax fon
- Ovoz effektlari va fon musiqasi (numpy orqali generatsiya qilinadi)
- Ekran aylantirilganda (rotatsiya) moslashadigan interfeys
- O'yin natijalarini saqlash (`cr7_save.json`)

## O'rnatish

```bash
git clone https://github.com/USERNAME/CR7-Jungle-Run.git
cd CR7-Jungle-Run
pip install -r requirements.txt
python main.py
```

## Boshqarish

| Amal | Klaviatura | Ekran (mobil) |
|---|---|---|
| Sakrash | Space / Up / W | "SAKRACH" tugmasi |
| Egilish | Down / S | "EGILISH" tugmasi |
| Pauza | Esc / P | Yuqori chap burchakdagi tugma |

## Papka tuzilishi

```
CR7-Jungle-Run/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── assets/
    └── player_sprites.png
```

> **Eslatma:** `player_sprites.png` fayli mavjud bo'lmasa, o'yin avtomatik ravishda oddiy geometrik shakllar bilan personajni chizadi (fallback rejimi).
>
> `cr7_save.json` o'yin ishga tushganda avtomatik yaratiladi, shuning uchun u repozitoriyaga qo'shilmaydi (`.gitignore`da ko'rsatilgan).

## Talablar

- Python 3.8+
- pygame
- numpy (ovoz effektlari uchun, ixtiyoriy — bo'lmasa o'yin ovozsiz ishlaydi)
