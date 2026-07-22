//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BuildInfo.mqh                                          |
//| Layer   : Common                                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Platform build information.                            |
//+------------------------------------------------------------------+
#ifndef CORE_COMMON_BUILDINFO_MQH
#define CORE_COMMON_BUILDINFO_MQH

//====================================================
// Platform Information
//====================================================

#define PLATFORM_NAME              "XAU AI PLATFORM"
#define PLATFORM_AUTHOR            "XAU AI Team"

//====================================================
// Version
//====================================================

#define BUILD_VERSION_MAJOR        1
#define BUILD_VERSION_MINOR        0
#define BUILD_VERSION_PATCH        0

//====================================================
// Build Number
//====================================================

#define BUILD_NUMBER               1

//====================================================
// Build Information
//====================================================

#define BUILD_DATE                 __DATE__
#define BUILD_TIME                 __TIME__

//====================================================
// Version String
//====================================================

#define PLATFORM_VERSION_STRING    "1.0.0"

//====================================================
// Build Configuration
//====================================================

#ifdef _DEBUG
   #define BUILD_CONFIGURATION "DEBUG"
#else
   #define BUILD_CONFIGURATION "RELEASE"
#endif

#endif // CORE_COMMON_BUILDINFO_MQH