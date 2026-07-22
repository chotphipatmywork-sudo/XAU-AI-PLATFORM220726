//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ErrorCodes.mqh                                         |
//| Layer   : Common                                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Standard error codes used across the platform.         |
//+------------------------------------------------------------------+
#ifndef CORE_COMMON_ERRORCODES_MQH
#define CORE_COMMON_ERRORCODES_MQH

//====================================================
// General
//====================================================

#define ERR_SUCCESS                        0
#define ERR_UNKNOWN                       -1

//====================================================
// Common
//====================================================

#define ERR_INVALID_PARAMETER           1000
#define ERR_NULL_POINTER                1001
#define ERR_OUT_OF_MEMORY               1002
#define ERR_NOT_IMPLEMENTED             1003
#define ERR_OPERATION_TIMEOUT           1004

//====================================================
// Kernel
//====================================================

#define ERR_KERNEL_ALREADY_INITIALIZED  2000
#define ERR_KERNEL_NOT_INITIALIZED      2001
#define ERR_KERNEL_ALREADY_RUNNING      2002
#define ERR_KERNEL_NOT_RUNNING          2003
#define ERR_KERNEL_INVALID_STATE        2004

//====================================================
// Module
//====================================================

#define ERR_MODULE_ALREADY_EXISTS       3000
#define ERR_MODULE_NOT_FOUND            3001
#define ERR_MODULE_INIT_FAILED          3002
#define ERR_MODULE_START_FAILED         3003
#define ERR_MODULE_STOP_FAILED          3004

//====================================================
// Event
//====================================================

#define ERR_EVENT_QUEUE_FULL            4000
#define ERR_EVENT_NOT_FOUND             4001
#define ERR_EVENT_DISPATCH_FAILED       4002

//====================================================
// Risk
//====================================================

#define ERR_RISK_LIMIT_EXCEEDED         5000
#define ERR_INVALID_LOT_SIZE            5001

//====================================================
// Trading
//====================================================

#define ERR_ORDER_SEND_FAILED           6000
#define ERR_ORDER_MODIFY_FAILED         6001
#define ERR_ORDER_CLOSE_FAILED          6002
#define ERR_POSITION_NOT_FOUND          6003

//====================================================
// AI Brain
//====================================================

#define ERR_BRAIN_NOT_READY             7000
#define ERR_MODEL_LOAD_FAILED           7001
#define ERR_PREDICTION_FAILED           7002

#endif // CORE_COMMON_ERRORCODES_MQH