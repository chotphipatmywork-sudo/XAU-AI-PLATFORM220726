//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TickMicrostructureEngine.mqh                           |
//| Layer   : Brain / Liquidity / Engines / Research                |
//| Version : 1.0.0                                                  |
//| Purpose : Encode ticks contained in one completed M15 bar        |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITY_ENGINES_TICKMICROSTRUCTUREENGINE_MQH
#define CORE_BRAIN_LIQUIDITY_ENGINES_TICKMICROSTRUCTUREENGINE_MQH

#include "../models/TickMicrostructureResult.mqh"

class CTickMicrostructureEngine
  {
private:
   double Price(const MqlTick &tick) const
     {
      return(0.5*(tick.bid+tick.ask));
     }

   double Bounded(const double value) const
     {
      return(MathMax(0.0,MathMin(100.0,value)));
     }

public:
   CTickMicrostructureResult Analyze(const MqlTick &ticks[],
                                     const double atr,
                                     const datetime barOpen,
                                     const ENUM_TIMEFRAMES timeframe) const
     {
      CTickMicrostructureResult result;
      const int count=ArraySize(ticks);
      result.TickCount=count;
      const int seconds=PeriodSeconds(timeframe);
      if(timeframe!=PERIOD_M15 || count<10 || atr<=0.0 ||
         barOpen<=0 || seconds<=0)
         return(result);

      const long firstMsc=(long)barOpen*1000;
      const long endMsc=(long)(barOpen+seconds)*1000;
      const int bucketCount=15;
      int buckets[];
      ArrayResize(buckets,bucketCount);
      ArrayInitialize(buckets,0);

      int up=0;
      int down=0;
      double spreadTotal=0.0;
      double spreadMaximum=0.0;
      double travel=0.0;
      double firstPrice=0.0;
      double previousPrice=0.0;

      for(int index=0; index<count; index++)
        {
         if(ticks[index].time_msc<firstMsc || ticks[index].time_msc>=endMsc ||
            ticks[index].bid<=0.0 || ticks[index].ask<=0.0 ||
            ticks[index].ask<ticks[index].bid)
            return(result);

         const double price=Price(ticks[index]);
         const double spread=ticks[index].ask-ticks[index].bid;
         spreadTotal+=spread;
         spreadMaximum=MathMax(spreadMaximum,spread);
         int bucket=(int)((ticks[index].time_msc-firstMsc)/60000);
         if(bucket<0)
            bucket=0;
         else if(bucket>=bucketCount)
            bucket=bucketCount-1;
         buckets[bucket]++;

         if(index==0)
           {
            firstPrice=price;
            previousPrice=price;
            continue;
           }
         const double change=price-previousPrice;
         travel+=MathAbs(change);
         if(change>0.0)
            up++;
         else if(change<0.0)
            down++;
         previousPrice=price;
        }

      const int directional=up+down;
      if(directional<=0 || travel<=0.0)
         return(result);

      int maximumBucket=0;
      for(int bucket=0; bucket<bucketCount; bucket++)
        {
         if(buckets[bucket]>maximumBucket)
            maximumBucket=buckets[bucket];
        }
      const double maximumShare=(double)maximumBucket/(double)count;
      const double uniformShare=1.0/(double)bucketCount;
      const double burst=100.0*(maximumShare-uniformShare)/(1.0-uniformShare);
      const double displacement=MathAbs(previousPrice-firstPrice);

      result.TickDirectionImbalance=Bounded(
         50.0+50.0*(double)(up-down)/(double)directional);
      result.TickBurstConcentration=Bounded(burst);
      result.MeanSpreadAtr=Bounded(100.0*(spreadTotal/(double)count)/atr);
      result.MaximumSpreadAtr=Bounded(100.0*spreadMaximum/atr);
      result.RealizedTickVolatilityAtr=Bounded(
         100.0*travel/(travel+10.0*atr));
      result.TickPathEfficiency=Bounded(100.0*displacement/travel);
      result.Valid=true;
      return(result);
     }
  };

#endif
