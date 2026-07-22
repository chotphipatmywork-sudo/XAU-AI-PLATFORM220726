//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Constants.mqh                                          |
//| Layer   : Common                                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Global platform constants.                             |
//+------------------------------------------------------------------+
#ifndef CORE_COMMON_CONSTANTS_MQH
#define CORE_COMMON_CONSTANTS_MQH

//====================================================
// Platform Information
//====================================================

#define PLATFORM_NAME              "XAU AI PLATFORM"
#define PLATFORM_AUTHOR            "XAU AI Team"

//====================================================
// Version
//====================================================

#define PLATFORM_VERSION_MAJOR     1
#define PLATFORM_VERSION_MINOR     0
#define PLATFORM_VERSION_PATCH     0

//====================================================
// Kernel
//====================================================

#define MAX_MODULE_COUNT           128

//====================================================
// Timing (milliseconds)
//====================================================

#define HEARTBEAT_INTERVAL_MS      1000
#define MODULE_TIMEOUT_MS          5000
#define WATCHDOG_INTERVAL_MS       1000

//====================================================
// Logging
//====================================================

#define MAX_LOG_MESSAGE_LENGTH     1024

//====================================================
// Queue
//====================================================

#define DEFAULT_QUEUE_SIZE         1024

//====================================================
// Memory
//====================================================

#define DEFAULT_BUFFER_SIZE        4096

#endif // CORE_COMMON_CONSTANTS_MQH