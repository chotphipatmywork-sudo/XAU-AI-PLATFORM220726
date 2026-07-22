//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskContext.mqh                                        |
//| Layer   : Core / Risk                                            |
//| Version : 2.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_RISKCONTEXT_MQH
#define CORE_RISK_RISKCONTEXT_MQH

class CRiskContext
{
public:

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;

   double Balance;

   double Equity;

   double FreeMargin;

   double Margin;

   double MarginLevel;

   double FloatingProfit;

   double FloatingLoss;

   double DailyProfit;

   double DailyLoss;

   double DrawdownPercent;

   double RiskPercent;

   double MaxRiskPercent;

   double MaxDrawdownPercent;

   bool AllowNewTrade;

   bool EmergencyStop;

   datetime CurrentTime;

   //--------------------------------------------------

   CRiskContext()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Symbol = "";

      Timeframe = PERIOD_CURRENT;

      Balance = 0.0;

      Equity = 0.0;

      FreeMargin = 0.0;

      Margin = 0.0;

      MarginLevel = 0.0;

      FloatingProfit = 0.0;

      FloatingLoss = 0.0;

      DailyProfit = 0.0;

      DailyLoss = 0.0;

      DrawdownPercent = 0.0;

      RiskPercent = 0.0;

      MaxRiskPercent = 0.0;

      MaxDrawdownPercent = 0.0;

      AllowNewTrade = true;

      EmergencyStop = false;

      CurrentTime = 0;
   }
};

#endif