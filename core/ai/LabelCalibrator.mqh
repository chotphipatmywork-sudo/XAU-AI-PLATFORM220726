//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LabelCalibrator.mqh                                    |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Measure triple-barrier label distributions safely      |
//+------------------------------------------------------------------+

#ifndef CORE_AI_LABELCALIBRATOR_MQH
#define CORE_AI_LABELCALIBRATOR_MQH

#include "LabelGenerator.mqh"
#include "models/LabelCalibrationReport.mqh"

class CLabelCalibrator
  {
public:
   bool Evaluate(const MqlRates &bars[],
                 const double &atr_values[],
                 const int horizon_bars,
                 const int atr_period,
                 const double barrier_atr_multiplier,
                 CLabelCalibrationReport &report) const
     {
      report.Reset();
      if(ArraySize(bars)<=0 || ArraySize(atr_values)!=ArraySize(bars))
         return(false);

      CLabelGenerator generator;
      if(!generator.Configure(horizon_bars,atr_period,barrier_atr_multiplier))
         return(false);

      report.HorizonBars=horizon_bars;
      report.AtrPeriod=atr_period;
      report.BarrierAtrMultiplier=barrier_atr_multiplier;
      for(int index=0; index<ArraySize(bars); index++)
        {
         ENUM_AI_TRAINING_LABEL label=AI_LABEL_HOLD;
         if(!generator.Generate(bars,index,atr_values[index],label))
           {
            report.ExcludedCount++;
            continue;
           }
         report.SampleCount++;
         if(label==AI_LABEL_BUY) report.BuyCount++;
         else if(label==AI_LABEL_HOLD) report.HoldCount++;
         else if(label==AI_LABEL_SELL) report.SellCount++;
        }
      return(report.SampleCount>0);
     }
  };

#endif
