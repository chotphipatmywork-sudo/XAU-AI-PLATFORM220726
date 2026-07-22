//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TelemetryLogger.mqh                                    |
//| Layer   : Core / Telemetry                                      |
//| Version : 1.0.0                                                  |
//| Purpose : Telemetry Logging Adapter                              |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_TELEMETRYLOGGER_MQH
#define CORE_TELEMETRY_TELEMETRYLOGGER_MQH


#include "models/TelemetrySnapshot.mqh"

#include "../infrastructure/Logger.mqh"


//--------------------------------------------------
// Telemetry Logger
//--------------------------------------------------

class CTelemetryLogger
{


public:


   //--------------------------------------------------
   // Log Snapshot
   //--------------------------------------------------

   void Log(
      const CTelemetrySnapshot &snapshot)
   {

      string message = "";


      message =
         "Telemetry | ";


      message +=
         "Symbol=" + snapshot.Symbol;


      message +=
         " | Running=" +
         (snapshot.Running ? "true" : "false");


      message +=
         " | Confidence=" +
         DoubleToString(
            snapshot.Confidence,
            2);


      message +=
         " | Risk=" +
         DoubleToString(
            snapshot.RiskScore,
            2);


      message +=
         " | Signals=" +
         IntegerToString(
            snapshot.TotalSignals);


      message +=
         " | Executions=" +
         IntegerToString(
            snapshot.Executions);


      message +=
         " | Rejections=" +
         IntegerToString(
            snapshot.Rejections);



      CLogger::Info(
         message);

   }


};


#endif

//+------------------------------------------------------------------+