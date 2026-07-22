//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalDatasetBuilder.mqh                           |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Persist replayed Brain features with historical labels |
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALDATASETBUILDER_MQH
#define CORE_AI_HISTORICALDATASETBUILDER_MQH

#include "AITrainingEngine.mqh"
#include "BrainFeatureAdapter.mqh"
#include "LabelGenerator.mqh"

class CHistoricalDatasetBuilder
  {
private:
   CBrainFeatureAdapter m_feature_adapter;
   CLabelGenerator      m_label_generator;

public:
   bool ConfigureLabeling(const int horizon_bars,const int atr_period,const double barrier_atr_multiplier)
     {
      return(m_label_generator.Configure(horizon_bars,atr_period,barrier_atr_multiplier));
     }

   bool BuildSample(const MqlRates &bars[],
                    const int index,
                    const CBrainAnalysisResult &analysis,
                    const double &atr_values[],
                    const string symbol,
                    CAITrainingEngine &training)
     {
      if(index<0 || index>=ArraySize(bars) || ArraySize(atr_values)!=ArraySize(bars))
         return(false);
      CAIFeatureVector features;
      if(!m_feature_adapter.Extract(analysis,features))
         return(false);
      ENUM_AI_TRAINING_LABEL label=AI_LABEL_HOLD;
      if(!m_label_generator.Generate(bars,index,atr_values[index],label))
         return(false);
      return(training.RecordSample(features,(double)label,symbol,bars[index].time));
     }

   // bars, analyses, and atr_values must share the same oldest-to-newest index.
   int Build(const MqlRates &bars[],const CBrainAnalysisResult &analyses[],const double &atr_values[],const string symbol,CAITrainingEngine &training)
     {
      const int count=ArraySize(bars);
      if(count<=0 || ArraySize(analyses)!=count || ArraySize(atr_values)!=count)
         return(0);
      int records_written=0;
      for(int index=0; index<count; index++)
        {
         if(BuildSample(bars,index,analyses[index],atr_values,symbol,training))
            records_written++;
        }
      return(records_written);
     }
  };

#endif
