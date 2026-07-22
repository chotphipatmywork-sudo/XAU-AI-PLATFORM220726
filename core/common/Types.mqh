//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Types.mqh                                              |
//| Layer   : Common                                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Shared type definitions used across the platform.       |
//+------------------------------------------------------------------+
#ifndef CORE_COMMON_TYPES_MQH
#define CORE_COMMON_TYPES_MQH

//====================================================
// Platform Version
//====================================================

#define XAU_AI_PLATFORM_VERSION_MAJOR   1
#define XAU_AI_PLATFORM_VERSION_MINOR   0
#define XAU_AI_PLATFORM_VERSION_PATCH   0

//====================================================
// Basic Result
//====================================================

enum ENUM_RESULT
{
   RESULT_SUCCESS = 0,
   RESULT_FAILED  = -1
};

//====================================================
// Kernel State
//====================================================

enum ENUM_KERNEL_STATE
{
   KERNEL_CREATED = 0,
   KERNEL_INITIALIZING,
   KERNEL_READY,
   KERNEL_RUNNING,
   KERNEL_STOPPING,
   KERNEL_STOPPED,
   KERNEL_FAULT
};

//====================================================
// Module State
//====================================================

enum ENUM_MODULE_STATE
{
   MODULE_CREATED = 0,
   MODULE_INITIALIZING,
   MODULE_READY,
   MODULE_RUNNING,
   MODULE_STOPPING,
   MODULE_STOPPED,
   MODULE_FAULT
};

//====================================================
// Health State
//====================================================

enum ENUM_HEALTH_STATE
{
   HEALTH_UNKNOWN = 0,
   HEALTH_OK,
   HEALTH_WARNING,
   HEALTH_ERROR,
   HEALTH_CRITICAL
};

//====================================================
// Module Information
//====================================================

struct SModuleInfo
{
   string             Name;
   string             Version;
   ENUM_MODULE_STATE  State;
   ENUM_HEALTH_STATE  Health;
};

//====================================================
// Version Information
//====================================================

struct SVersionInfo
{
   int Major;
   int Minor;
   int Patch;
};

#endif // CORE_COMMON_TYPES_MQH