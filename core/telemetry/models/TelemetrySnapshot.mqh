//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TelemetrySnapshot.mqh                                  |
//| Layer   : Core / Telemetry / Models                              |
//| Version : 1.0.0                                                  |
//| Purpose : Telemetry Snapshot Model                               |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_MODELS_TELEMETRYSNAPSHOT_MQH
#define CORE_TELEMETRY_MODELS_TELEMETRYSNAPSHOT_MQH


//--------------------------------------------------
// Telemetry Snapshot
//--------------------------------------------------

class CTelemetrySnapshot
{

public:

   //--------------------------------------------------
   // Runtime State
   //--------------------------------------------------

   bool Running;

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;



   //--------------------------------------------------
   // Module Status
   //--------------------------------------------------

   bool BrainReady;

   bool AIReady;

   bool RiskReady;

   bool ExecutionReady;

   bool TradeReady;



   //--------------------------------------------------
   // Execution Data
   //--------------------------------------------------

   int TotalSignals;

   int Executions;

   int Rejections;



   //--------------------------------------------------
   // Performance Data
   //--------------------------------------------------

   double Confidence;

   double RiskScore;



   //--------------------------------------------------
   // Timestamp
   //--------------------------------------------------

   datetime Timestamp;



   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CTelemetrySnapshot()
   {
      Reset();
   }



   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {

      Running = false;


      Symbol = "";

      Timeframe = PERIOD_CURRENT;


      BrainReady = false;

      AIReady = false;

      RiskReady = false;

      ExecutionReady = false;

      TradeReady = false;


      TotalSignals = 0;

      Executions = 0;

      Rejections = 0;


      Confidence = 0.0;

      RiskScore = 0.0;


      Timestamp = 0;

   }

};


#endif

//+------------------------------------------------------------------+