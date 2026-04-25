# Idea Reference — xwdata (REF_12_IDEA)

**Library:** exonware-xwdata  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) (GUIDE_01_REQ)  
**Producing guide:** [GUIDE_12_IDEA.md](../../docs/guides/GUIDE_12_IDEA.md)

---

## Purpose

Idea context and evaluation for xwdata, filled from REF_01_REQ. Used for traceability from idea → requirements → project.

---

## Core Idea (from REF_01_REQ sec. 1–2)

| Field | Content |
|-------|---------|
| **Problem statement** | When we want to create other libraries we don’t need to worry about save/load and the optimization of that. xwdata handles it; it can even play as a database (front-end or backend). |
| **Solution direction** | Linking xwnode with xwobject and serialization — all combined creates xwdata. Data structure using xwnode; reference and reference capabilities; lazy capabilities (extended from serialization or xwnode). Only the data structure. |
| **One-sentence purpose** | xwdata is an implementation of xwnode plus serialization: enabling serializations (JSON, TOML, and more) to be saved as data nodes; it is the base of any data structure and will be used for saving data, getting data, and many data operations. |
| **Primary beneficiaries** | Developers; xwschema, xwaction, xwentity, xwstorage.connect and others. Extends XW object (xwsystem) by linking xwnode capabilities and serialization. |
| **Top goals (ordered)** | (1) Support for all serialization formats in ExonWare. (2) Save/load efficiently — performance. (3) Extensibility. (4) So other libraries don’t worry about save/load. (5) xwdata can play as a database; links xwnode + xwobject + serialization. |
| **Out of scope** | Concrete schema; actions; xwentity features; node/edge strategies (in xwnode). xwdata only mixes xwobject + xwnode + serialization. |

---

## Evaluation

| Criterion | Assessment |
|-----------|------------|
| **Status** | Approved (implemented; REF_01_REQ clarity 14/14). |
| **Five Priorities** | Security, Usability, Maintainability, Performance, Extensibility — addressed in REF_01_REQ sec. 8 and implemented (config, tests, engine pattern). |
| **Traceability** | REF_01_REQ → REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, REF_21_PLAN. |

---

*See REF_01_REQ.md for full requirements. See REF_22_PROJECT.md for project status. **Consumers:** xwschema, xwaction, xwentity, xwstorage.connect, xwquery — see [REF_22_PROJECT](REF_22_PROJECT.md) traceability.*
