//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DrawdownProtection.mqh                                 |
//| Layer   : Core / Risk                                            |
//| Version : 1.0.0                                                  |
//| Purpose : Drawdown Protection                                    |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_DRAWDOWNPROTECTION_MQH
#define CORE_RISK_DRAWDOWNPROTECTION_MQH

class CDrawdownProtection
{
private:

   double m_maxDrawdownPercent;

public:

   CDrawdownProtection()
   {
      m_maxDrawdownPercent = 10.0;
   }

   void SetLimit(const double percent)
   {
      if(percent > 0.0)
         m_maxDrawdownPercent = percent;
   }

   double GetLimit() const
   {
      return m_maxDrawdownPercent;
   }

   double CurrentDrawdown() const
   {
      double balance =
         AccountInfoDouble(ACCOUNT_BALANCE);

      double equity =
         AccountInfoDouble(ACCOUNT_EQUITY);

      if(balance <= 0.0)
         return 0.0;

      return ((balance - equity) / balance) * 100.0;
   }

   bool AllowTrading() const
   {
      return CurrentDrawdown() < m_maxDrawdownPercent;
   }
};

#endif