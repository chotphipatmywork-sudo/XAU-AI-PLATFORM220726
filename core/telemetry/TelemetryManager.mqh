//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TelemetryManager.mqh                                   |
//| Layer   : Core / Telemetry                                       |
//| Version : 2.0.0                                                  |
//| Purpose : Telemetry State Manager                                |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_TELEMETRYMANAGER_MQH
#define CORE_TELEMETRY_TELEMETRYMANAGER_MQH


#include "models/TelemetrySnapshot.mqh"
#include "TelemetryLogger.mqh"


//--------------------------------------------------
// Telemetry Manager
//--------------------------------------------------

class CTelemetryManager
{

private:

   ulong m_ticks;

   ulong m_trades;

   datetime m_lastUpdate;


   CTelemetryLogger m_logger;



public:


   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CTelemetryManager()
   {
      Reset();
   }



   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {

      m_ticks = 0;

      m_trades = 0;

      m_lastUpdate = 0;

   }



   //--------------------------------------------------
   // Tick Event
   //--------------------------------------------------

   void OnTick()
   {

      m_ticks++;

      m_lastUpdate =
         TimeCurrent();

   }



   //--------------------------------------------------
   // Trade Event
   //--------------------------------------------------

   void OnTrade()
   {

      m_trades++;

      m_lastUpdate =
         TimeCurrent();

   }



   //--------------------------------------------------
   // Create Snapshot
   //--------------------------------------------------

   CTelemetrySnapshot Capture() const
   {

      CTelemetrySnapshot snapshot;


      snapshot.Timestamp =
         m_lastUpdate;


      snapshot.TotalSignals =
         (int)m_ticks;


      snapshot.Executions =
         (int)m_trades;


      snapshot.Running = true;


      return snapshot;

   }



   //--------------------------------------------------
   // Log Snapshot
   //--------------------------------------------------

   void Log()
   {

      CTelemetrySnapshot snapshot =
         Capture();


      m_logger.Log(
         snapshot);

   }



   //--------------------------------------------------
   // Tick Count
   //--------------------------------------------------

   ulong TickCount() const
   {
      return m_ticks;
   }



   //--------------------------------------------------
   // Trade Count
   //--------------------------------------------------

   ulong TradeCount() const
   {
      return m_trades;
   }



   //--------------------------------------------------
   // Last Update
   //--------------------------------------------------

   datetime LastUpdate() const
   {
      return m_lastUpdate;
   }


};


#endif

//+------------------------------------------------------------------+