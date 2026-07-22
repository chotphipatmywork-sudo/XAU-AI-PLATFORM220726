//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalDatasetBuilder.mq5                       |
//| Layer   : Tests / AI / Learning                                  |
//| Version : 4.0.0                                                  |
//| Purpose : Historical dataset builder smoke test                  |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/HistoricalDatasetBuilder.mqh"

void OnStart()
  {
   MqlRates bars[];
   CBrainAnalysisResult analyses[];
   double atr_values[];
   ArrayResize(bars,17);
   ArrayResize(analyses,17);
   ArrayResize(atr_values,17);

   for(int index=0; index<17; index++)
     {
      bars[index].time=TimeCurrent()+index*PeriodSeconds(PERIOD_M15);
      bars[index].close=100.0;
      bars[index].high=101.0;
      bars[index].low=99.0;
      analyses[index].Valid=true;
      analyses[index].Trend.Strength=50.0;
      analyses[index].Trend.AITrendRegime=55.0;
      analyses[index].Trend.AITrendMomentum=50.0;
      analyses[index].Trend.AITrendSlope=45.0;
      analyses[index].Volatility.AIVolatilityRegime=50.0;
      analyses[index].Volatility.AIVolatilityChange=50.0;
      analyses[index].Liquidity.Score=50.0;
      analyses[index].Liquidity.RangePosition=50.0;
      analyses[index].Liquidity.SweepDirection=50.0;
      analyses[index].Session.State=SESSION_LONDON;
      analyses[index].Session.Progress=25.0;
      atr_values[index]=10.0;
     }
   bars[1].high=111.0;

   CAITrainingEngine training;
   if(!training.Initialize())
     {
      Print("Training initialization failed");
      return;
     }

   CHistoricalDatasetBuilder builder;
   const int records_written=builder.Build(bars,analyses,atr_values,_Symbol,training);
   Print("Historical dataset records written: ",records_written);
   training.Shutdown();
  }
