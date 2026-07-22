//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EquityProtection.mqh                                   |
//| Layer   : Core / Risk                                            |
//| Version : 1.0.0                                                  |
//| Purpose : Equity Protection                                      |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_EQUITYPROTECTION_MQH
#define CORE_RISK_EQUITYPROTECTION_MQH

class CEquityProtection
{
private:

   double m_minEquityPercent;

public:

   CEquityProtection()
   {
      m_minEquityPercent = 90.0;
   }

   void SetMinimumEquity(const double percent)
   {
      if(percent > 0.0 && percent <= 100.0)
         m_minEquityPercent = percent;
   }

   double GetMinimumEquity() const
   {
      return m_minEquityPercent;
   }

   double CurrentEquityPercent() const
   {
      double balance =
         AccountInfoDouble(ACCOUNT_BALANCE);

      double equity =
         AccountInfoDouble(ACCOUNT_EQUITY);

      if(balance <= 0.0)
         return 0.0;

      return (equity / balance) * 100.0;
   }

   bool AllowTrading() const
   {
      return CurrentEquityPercent() >=
             m_minEquityPercent;
   }
};

#endif