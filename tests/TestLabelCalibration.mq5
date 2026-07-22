//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestLabelCalibration.mq5                               |
//| Purpose : Historical triple-barrier label calibration test       |
//+------------------------------------------------------------------+

#property strict

#include "../core/data/HistoricalDataProvider.mqh"
#include "../core/ai/LabelCalibrator.mqh"

input int DatasetBars=5000;
input int HorizonBars=16;
input int AtrPeriod=14;
input double BarrierOne=1.00;
input double BarrierTwo=1.25;
input double BarrierThree=1.50;

void PrintReport(const CLabelCalibrationReport &report)
  {
   Print("Label calibration barrier ",report.BarrierAtrMultiplier,
         " ATR | samples: ",report.SampleCount,
         " | BUY/HOLD/SELL: ",report.BuyCount,"/",report.HoldCount,"/",report.SellCount,
         " | HOLD ratio: ",DoubleToString(report.HoldRatio()*100.0,2),"%",
         " | excluded: ",report.ExcludedCount);
  }

int OnInit()
  {
   if(DatasetBars<=0 || HorizonBars<=0 || AtrPeriod<=0 ||
      BarrierOne<=0.0 || BarrierTwo<=0.0 || BarrierThree<=0.0)
      return(INIT_PARAMETERS_INCORRECT);

   const datetime to=TimeCurrent();
   const datetime from=to-DatasetBars*PeriodSeconds(PERIOD_M15);
   CHistoricalDataProvider provider;
   MqlRates bars[];
   double atr_values[];
   const int rates_copied=provider.LoadRates(_Symbol,PERIOD_M15,from,to,bars);
   const int atr_copied=provider.LoadAtr(_Symbol,PERIOD_M15,AtrPeriod,from,to,atr_values);
   if(rates_copied<=0 || atr_copied!=rates_copied)
     {
      Print("Label calibration data load failed");
      return(INIT_FAILED);
     }

   CLabelCalibrator calibrator;
   CLabelCalibrationReport report;
   if(!calibrator.Evaluate(bars,atr_values,HorizonBars,AtrPeriod,BarrierOne,report)) return(INIT_FAILED);
   PrintReport(report);
   if(!calibrator.Evaluate(bars,atr_values,HorizonBars,AtrPeriod,BarrierTwo,report)) return(INIT_FAILED);
   PrintReport(report);
   if(!calibrator.Evaluate(bars,atr_values,HorizonBars,AtrPeriod,BarrierThree,report)) return(INIT_FAILED);
   PrintReport(report);
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
