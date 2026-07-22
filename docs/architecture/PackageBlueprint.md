# XAU AI PLATFORM - Package Blueprint

Version: 1.1.0

Status: Foundation

Architecture Baseline: ABR-1.0

---

## Purpose

เอกสารนี้กำหนดมาตรฐานโครงสร้าง Package สำหรับ XAU-AI-PLATFORM

เป้าหมาย:

- ให้ทุก Package มีรูปแบบเดียวกัน
- ลดความซับซ้อนในการพัฒนา
- ควบคุม Dependency
- ทำให้ Repository มีมาตรฐานเดียวกัน
- รองรับการขยายระบบในอนาคต
- เป็นแนวทางสำหรับนักพัฒนาและ AI Coding Assistant

---

## Package Concept

Package คือหน่วยความรับผิดชอบทางสถาปัตยกรรม (Architectural Unit)

ทุก Package ต้องมี:

- Defined Responsibility
- Explicit Boundary
- Stable Contract
- Stable Result Object
- Controlled Dependency

หนึ่ง Package ต้องรับผิดชอบเพียงหน้าที่เดียว

---

## Standard Package Structure

```text
PackageName/
│
├── config/
├── models/
├── engines/
├── assembler/
├── services/
├── analyzer/
├── manager/
└── tests/

โครงสร้างนี้เป็นมาตรฐานอ้างอิงของทุก Package

Optional Folder Rule

ไม่จำเป็นต้องมีทุกโฟลเดอร์

อนุญาตให้เลือกเฉพาะสิ่งที่จำเป็นตาม Responsibility ของ Package

ตัวอย่าง:

brain/

├── config/
├── models/
├── engines/
├── assembler/
└── analyzer/

ถือว่าเป็นโครงสร้างที่ถูกต้อง

ห้ามสร้างโฟลเดอร์ที่ไม่มีหน้าที่ชัดเจน

Package Contract

ทุก Package ต้องกำหนด Contract ก่อนเริ่มพัฒนา

Contract ต้องประกอบด้วย:

Purpose

Package ทำหน้าที่อะไร

Input

รับข้อมูลจาก Package ใด

Output

ส่งข้อมูลให้ Package ใด

Public API

ไฟล์ที่ Package อื่นสามารถเรียกใช้ได้

Internal Files

ไฟล์ที่ห้ามเรียกใช้จากภายนอก

Dependencies

Package ที่อนุญาตให้อ้างอิง

Forbidden Dependencies

Package ที่ห้ามอ้างอิง

Package Contract ถือเป็นส่วนหนึ่งของ Architecture Documentation

Folder Responsibility
config

หน้าที่:

เก็บ Configuration

ตัวอย่าง:

RiskConfig
TrendConfig

Rule:

ไม่มี Business Logic
ไม่มี Runtime State
models

หน้าที่:

เก็บ Data Object

ตัวอย่าง:

TrendResult
RiskResult
DecisionResult

Rule:

Model ไม่มี Business Logic
Model เป็น Data Container เท่านั้น
engines

หน้าที่:

ประมวลผล Business Logic เฉพาะด้าน

Rule:

One Engine = One Responsibility

ตัวอย่าง:

TrendEngine
VolatilityEngine
LiquidityEngine
assembler

หน้าที่:

รวมผลลัพธ์จากหลาย Engine

Assembler สามารถ:

Combine Result
Build Output Object
Normalize Result

Assembler ห้าม:

คำนวณ Indicator
วิเคราะห์ตลาด
ตัดสินใจซื้อขาย
services

หน้าที่:

Utility ภายใน Package

ตัวอย่าง:

Validator
Filter
Normalizer

Services ไม่ควรถูกเรียกจากภายนอก Package

analyzer

หน้าที่:

เป็น Public Facade ของ Package

Responsibilities:

Execute Engines
Manage Workflow
Call Assembler
Return Package Result

Analyzer เป็น Orchestrator เท่านั้น

Analyzer ไม่มี Business Logic

manager

หน้าที่:

จัดการ Lifecycle ของ Package

Responsibilities:

Initialize
Configure
Update
Reset
Shutdown

Manager ไม่แทนที่ Analyzer

tests

ใช้สำหรับ:

Unit Test
Integration Test
Validation Test

ทุก Package ควรสามารถทดสอบได้อย่างอิสระ

---

## Dependency Direction

Package Dependency ต้องไหลตามลำดับดังนี้:

```text
Config
    │
    ▼
Models
    │
    ▼
Engines
    │
    ▼
Assembler
    │
    ▼
Analyzer
    │
    ▼
Manager
    │
    ▼
External Package
Dependency Rules

Dependencies must always follow these rules:

Dependencies must always flow downward.
Reverse Dependency is prohibited.
Circular Dependency is prohibited.
Hidden Dependency is prohibited.
Cross-layer Dependency is prohibited unless explicitly documented.
Every dependency must be documented.

ตัวอย่างที่ไม่อนุญาต:

Models
    │
    └────────────► Engine

หรือ:

Analyzer
        ▲
        │
     Engine

เนื่องจากทำให้เกิด Reverse Dependency

Package Lifecycle

ทุก Package ควรมีวงจรชีวิต (Lifecycle) ที่สอดคล้องกัน:

Initialize

↓

Configure

↓

Execute

↓

Update

↓

Reset

↓

Shutdown
Initialize

หน้าที่:

สร้างทรัพยากรเริ่มต้น
ตรวจสอบความพร้อม
Configure

หน้าที่:

โหลด Configuration
ตั้งค่าการทำงาน
Execute

หน้าที่:

ประมวลผลหน้าที่หลักของ Package
Update

หน้าที่:

อัปเดตข้อมูล Runtime
Reset

หน้าที่:

คืนค่าภายใน Package
Shutdown

หน้าที่:

ปล่อยทรัพยากร
ปิดการทำงานอย่างปลอดภัย
Package Result Rule

ทุก Package ต้องมี Result Object หลักเพียงหนึ่งชนิด

ตัวอย่าง:

TrendResult
VolatilityResult
LiquidityResult
RiskResult
DecisionResult
ExecutionResult

Package อื่นต้องสื่อสารผ่าน Result Object

กฎ:

ห้ามส่ง Internal Object ออกนอก Package
Result Object ถือเป็น Stable Contract
Package Interface Rule

ทุก Package ต้องมี Public Entry Point เพียงจุดเดียว

ตัวอย่าง:

PackageAnalyzer
PackageManager

External Package สามารถเรียกใช้เฉพาะ:

Analyzer
Manager
Public Models

ห้ามเรียก:

Internal Engines
Internal Services
Internal Assemblers
Private Implementations

การเข้าถึงภายใน Package ต้องผ่าน Public Contract เท่านั้น

Package Versioning

ทุก Package ควรระบุ:

Version
Status
Baseline Compatibility

ตัวอย่าง:

Version : 1.2.0

Status : Stable

Baseline : ABR-1.0
Breaking Changes

การเปลี่ยนแปลงต่อไปนี้ต้องผ่าน Architecture Review ก่อนเสมอ:

เปลี่ยน Public API
เปลี่ยน Result Object
เปลี่ยน Dependency
เปลี่ยน Contract
Required Package Documents

ทุก Package ควรมีเอกสารประกอบอย่างน้อย:

Package Contract
Dependency Diagram
Public API
Result Model

เมื่อ Package มีความซับซ้อนเพิ่มขึ้น ควรมี:

Sequence Diagram
State Diagram
Design Notes

Documentation ถือเป็นส่วนหนึ่งของ Package

---

## Package Review Process

ทุก Package ใหม่ต้องผ่านขั้นตอน:

```text
Proposal

↓

Architecture Review

↓

Approval

↓

Implementation

↓

Compile

↓

Validation

↓

Documentation Review

↓

Merge

ห้าม Merge Package ที่ยังไม่ผ่าน Validation

Package Iron Rules

กฎต่อไปนี้เป็น Architecture Constraint ถาวรของ XAU AI PLATFORM

Rule 1

One Responsibility

Rule 2

One Class Per File

Rule 3

One Package One Result

Rule 4

Workspace Has No Business Logic

Rule 5

Assembler Has No Calculation Logic

Rule 6

Analyzer Is Only Orchestrator

Rule 7

Package Result Is Stable Contract

Rule 8

Every Dependency Must Be Explicit

Rule 9

Every Package Must Expose One Public Entry Point

Rule 10

Architecture First

Implementation Second

Package Review Checklist

ก่อนเพิ่ม Package ใหม่ ต้องตรวจสอบ:

Architecture
Purpose ชัดเจน
Contract ครบถ้วน
Dependency ถูกต้อง
Public API ถูกกำหนด
Implementation
Folder Structure ถูกต้อง
Naming Convention ถูกต้อง
Compile ผ่าน
Quality
ไม่มี Duplicate Logic
ไม่มี Hidden Dependency
Result Object มีความเสถียร
Documentation ครบถ้วน

ทุกหัวข้อต้องผ่านก่อน Merge

Document Status

Version:

1.1.0

Status:

Foundation

Architecture Baseline:

ABR-1.0

Document Status:

Approved Foundation Blueprint

End of Package Blueprint
