//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Application.mqh                                        |
//| Layer   : Kernel                                                 |
//| Version : 4.2.0                                                  |
//| Purpose : Application Entry Point                                |
//+------------------------------------------------------------------+

#ifndef CORE_KERNEL_APPLICATION_MQH
#define CORE_KERNEL_APPLICATION_MQH

#include "../system/SystemManager.mqh"
#include "../runtime/models/ShadowRuntimeConfig.mqh"

//--------------------------------------------------

class CApplication
{
private:

   CSystemManager m_system;

public:

   //--------------------------------------------------

   bool Initialize()
   {
      CShadowRuntimeConfig config;
      return Initialize(config);
   }

   bool Initialize(const CShadowRuntimeConfig &config)
   {
      return m_system.Initialize(config);
   }

   //--------------------------------------------------

   bool Run(
      const string symbol,
      ENUM_TIMEFRAMES timeframe)
   {
      return m_system.Update(
         symbol,
         timeframe);
   }

   //--------------------------------------------------

   void OnTimer()
   {
      m_system.OnTimer();
   }

   //--------------------------------------------------

   void Shutdown()
   {
      m_system.Shutdown();
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_system.SetEmergencyStop(enabled);
   }

   void CaptureShadowBacktestReport(CShadowBacktestReport &report,
                                    const datetime startTime,
                                    const datetime endTime,
                                    const bool brokerStateUnchanged) const
   {
      m_system.CaptureShadowBacktestReport(
         report,startTime,endTime,brokerStateUnchanged);
   }

   //--------------------------------------------------

   CSystemManager* System()
   {
      return &m_system;
   }

};

#endif
