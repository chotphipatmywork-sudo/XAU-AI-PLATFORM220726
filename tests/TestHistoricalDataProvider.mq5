//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalDataProvider.mq5                         |
//| Purpose : Historical data provider smoke test                    |
//+------------------------------------------------------------------+

#property strict

#include "../core/data/HistoricalDataProvider.mqh"

void OnStart()
  {
   const datetime to=TimeCurrent();
   const datetime from=to-30*PeriodSeconds(PERIOD_M15);
   MqlRates rates[];
   double atr_values[];
   CHistoricalDataProvider provider;
   const int rates_copied=provider.LoadRates(_Symbol,PERIOD_M15,from,to,rates);
   const int atr_copied=provider.LoadAtr(_Symbol,PERIOD_M15,14,from,to,atr_values);
   Print("Historical rates: ",rates_copied," ATR values: ",atr_copied);
  }
