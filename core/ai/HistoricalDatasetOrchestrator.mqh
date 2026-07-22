//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalDatasetOrchestrator.mqh                      |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Stream replayed historical Brain output into a dataset |
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALDATASETORCHESTRATOR_MQH
#define CORE_AI_HISTORICALDATASETORCHESTRATOR_MQH

#include "../data/HistoricalDataProvider.mqh"
#include "../brain/HistoricalBrainReplay.mqh"
#include "AITrainingEngine.mqh"
#include "HistoricalDatasetBuilder.mqh"

class CHistoricalDatasetOrchestrator
  {
private:
   CHistoricalDataProvider  m_data_provider;
   CHistoricalBrainReplay   m_brain_replay;
   CHistoricalDatasetBuilder m_dataset_builder;

public:
   bool ConfigureLabeling(const int horizon_bars,const int atr_period,const double barrier_atr_multiplier)
     {
      return(m_dataset_builder.ConfigureLabeling(horizon_bars,atr_period,barrier_atr_multiplier));
     }

   int Build(const string symbol,
             const ENUM_TIMEFRAMES timeframe,
             const datetime from,
             const datetime to,
             const bool append_dataset=false,
             const int progress_interval=0)
     {
      MqlRates rates[];
      double atr_values[];
      const int rates_copied=m_data_provider.LoadRates(symbol,timeframe,from,to,rates);
      const int atr_copied=m_data_provider.LoadAtr(symbol,timeframe,14,from,to,atr_values);
      if(rates_copied<=0 || atr_copied!=rates_copied)
         return(0);

      CAITrainingEngine training;
      if(!training.Initialize(append_dataset))
         return(0);

      int records_written=0;
      for(int index=0; index<rates_copied; index++)
        {
         const int shift=iBarShift(symbol,timeframe,rates[index].time,true);
         if(shift<0)
           {
            training.Shutdown();
            return(0);
           }
         const CBrainAnalysisResult analysis=m_brain_replay.Analyze(symbol,timeframe,shift);
         if(m_dataset_builder.BuildSample(rates,index,analysis,atr_values,symbol,training))
            records_written++;
         if(progress_interval>0 && ((index+1)%progress_interval==0 || index+1==rates_copied))
           {
            training.Flush();
            Print("Historical dataset progress: ",index+1,"/",rates_copied,
                  " bars, records written: ",records_written);
           }
        }
      training.Flush();
      training.Shutdown();
      return(records_written);
     }
  };

#endif
