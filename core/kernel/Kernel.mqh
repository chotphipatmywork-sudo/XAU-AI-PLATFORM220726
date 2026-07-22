//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Kernel.mqh                                             |
//| Layer   : Kernel                                                 |
//| Version : 3.3.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_KERNEL_KERNEL_MQH
#define CORE_KERNEL_KERNEL_MQH

#include "Application.mqh"

//--------------------------------------------------

class CKernel
{
private:

   CApplication m_application;

public:

   //--------------------------------------------------

   bool Initialize()
   {
      CShadowRuntimeConfig config;
      return Initialize(config);
   }

   bool Initialize(const CShadowRuntimeConfig &config)
   {
      return m_application.Initialize(config);
   }

   //--------------------------------------------------

   bool Tick(
      const string symbol,
      ENUM_TIMEFRAMES timeframe)
   {
      return m_application.Run(
         symbol,
         timeframe);
   }

   //--------------------------------------------------
   // Timer
   //--------------------------------------------------

   void OnTimer()
   {
      m_application.OnTimer();
   }

   //--------------------------------------------------

   void Shutdown()
   {
      m_application.Shutdown();
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_application.SetEmergencyStop(enabled);
   }

   void CaptureShadowBacktestReport(CShadowBacktestReport &report,
                                    const datetime startTime,
                                    const datetime endTime,
                                    const bool brokerStateUnchanged) const
   {
      m_application.CaptureShadowBacktestReport(
         report,startTime,endTime,brokerStateUnchanged);
   }
};

#endif
