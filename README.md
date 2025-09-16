# MedQueue

سیستم نوبت‌دهی آنلاین پزشکان  
پروژه‌ای برای مدیریت و رزرو نوبت‌های ویزیت پزشکان توسط بیماران به صورت آنلاین.


## Features

- 👩‍⚕️ مدیریت پزشکان توسط ادمین‌ها (افزودن پزشک، تخصص و زمان‌های آزاد)
- 🔍 جستجوی پزشک بر اساس نام یا تخصص
- 📅 رزرو نوبت از بین زمان‌های آزاد پزشک
- 💳 پرداخت هزینه ویزیت از طریق کیف پول
- 📧 ارسال تاییدیه رزرو از طریق ایمیل
- ⭐ امکان نظردهی و امتیازدهی به پزشکان
- 🔑 احراز هویت با سیستم Django Auth و OTP
- 🔐 ورود با حساب گوگل (OAuth2)
- 🐳 پشتیبانی از docker
- ⚙️ تنظیمات محیطی با `.env`

## مراحل راه‌اندازی

### کلون کردن پروژه

```bash
  git clone https://github.com/Alikhoshakhlagh/MedQueue.git
  cd MedQueue
```
### ایجاد و فعال‌سازی virtualenv
```bash
  python -m venv venv
  source venv/bin/activate   
```
### نصب وابستگی‌ها
```bash
  pip install -r requirements.txt  
```
## اجرا

برای اجرای این پروژه
### فایل env.
```bash
  cp .env.example .env  
```
### ساخت ایمیج‌ها و اجرای کانتینرها
```bash
  docker-compose up --build 
```

## Authors

- [@Alikhoshakhlagh](https://github.com/Alikhoshakhlagh)
- [@Taha](https://github.com/Tahash44)
- [@aliakbari](https://github.com/aliakbari77)
- [@Mehrshad](https://github.com/Mehrshad3)
- [@pourya](https://github.com/pouryaenayati)
- [@MohammadHosein](https://github.com/fathali-codes)


