//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskAnalyzer.mqh                                       |
//| Layer   : Core / Risk                                            |
//| Version : 1.3.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_RISKANALYZER_MQH
#define CORE_RISK_RISKANALYZER_MQH

#include "DailyLossTracker.mqh"
#include "DrawdownProtection.mqh"
#include "EquityProtection.mqh"


class CRiskAnalyzer
{
private:

   CDailyLossTracker   m_dailyLoss;

   CDrawdownProtection m_drawdown;

   CEquityProtection   m_equity;

   double              m_maxDailyLossPercent;

   bool                m_emergencyStop;


public:


   CRiskAnalyzer()
   {
      m_maxDailyLossPercent = 5.0;
      m_emergencyStop = false;
   }

   void SetMaxDailyLossPercent(const double percent)
   {
      if(percent > 0.0)
         m_maxDailyLossPercent = percent;
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_emergencyStop = enabled;
   }

   bool EmergencyStopEnabled() const
   {
      return m_emergencyStop;
   }



   void Update()
   {
      m_dailyLoss.Update();
   }



   bool AllowTrading()
   {
      Update();

      if(m_emergencyStop)
         return false;

      if(m_dailyLoss.GetDailyLossPercent() >= m_maxDailyLossPercent)
         return false;

      if(!m_drawdown.AllowTrading())
         return false;


      if(!m_equity.AllowTrading())
         return false;


      return true;
   }



   double DailyLossPercent()
   {
      return m_dailyLoss.GetDailyLossPercent();
   }



   double DrawdownPercent()
   {
      return m_drawdown.CurrentDrawdown();
   }



   double EquityPercent()
   {
      return m_equity.CurrentEquityPercent();
   }

};


#endif
