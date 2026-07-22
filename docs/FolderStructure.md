# XAU AI PLATFORM

# Folder Structure

```
XAU AI PLATFORM
│
├── core
│   │
│   ├── brain
│   │
│   ├── market
│   │
│   ├── execution
│   │
│   ├── risk
│   │
│   └── utils
│
├── tests
│
├── docs
│
└── experts
```

---

# Folder Description

## core/

Business Logic ทั้งหมด

ไม่มีไฟล์สำหรับทดสอบ

ไม่มี EA

---

## core/brain/

AI Brain ทั้งหมด

ประกอบด้วย

- Brain
- Context
- Signal
- Decision
- Analyzer
- Score Engine
- Signal Engine

---

## core/market/

รับข้อมูลจากตลาด

เช่น

- Bid
- Ask
- Spread
- OHLC
- Tick

---

## core/risk/

บริหารความเสี่ยง

เช่น

- Risk Engine
- Money Manager
- Equity Protection

---

## core/execution/

ส่งคำสั่งซื้อขาย

ไม่มี Logic วิเคราะห์

---

## core/utils/

Utility

Library

Function กลาง

---

## tests/

ไฟล์สำหรับ Compile Test

Unit Test

Integration Test

ห้ามใช้ใน Production

---

## docs/

เอกสารทั้งหมดของโปรเจกต์

Architecture

Coding Standard

Iron Rules

Roadmap

---

## experts/

EA หลัก

สำหรับ MT5

Production Entry Point

---

# Folder Policy

- แยก Layer อย่างชัดเจน
- ห้าม Cross Layer โดยไม่จำเป็น
- Utility ต้องไม่มี Business Logic
- Test แยกจาก Production

---

Version

Foundation 1.0