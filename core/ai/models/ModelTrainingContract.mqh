//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ModelTrainingContract.mqh                              |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Define the stable offline model training contract      |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_MODELTRAININGCONTRACT_MQH
#define CORE_AI_MODELS_MODELTRAININGCONTRACT_MQH

class CModelTrainingContract
  {
public:
   string ModelName(void) const { return("XAU_AI_CLASSIFIER"); }
   string ContractVersion(void) const { return("4.0.0"); }
   string FeatureSchemaVersion(void) const { return("4.0.0"); }
   string LabelSchemaVersion(void) const { return("1.1.0"); }
   string InputName(void) const { return("features"); }
   string OutputName(void) const { return("class_probabilities"); }
   int FeatureCount(void) const { return(12); }
   int ClassCount(void) const { return(3); }

   string FeatureName(const int index) const
     {
      if(index==0) return("trend_regime");
      if(index==1) return("trend_momentum");
      if(index==2) return("trend_slope");
      if(index==3) return("volatility_regime");
      if(index==4) return("volatility_change");
      if(index==5) return("liquidity_activity");
      if(index==6) return("liquidity_range_position");
      if(index==7) return("liquidity_sweep_direction");
      if(index==8) return("session_asia");
      if(index==9) return("session_london");
      if(index==10) return("session_new_york");
      if(index==11) return("session_progress");
      return("");
     }

   string ClassName(const int index) const
     {
      if(index==0) return("SELL");
      if(index==1) return("HOLD");
      if(index==2) return("BUY");
      return("");
     }

   int ClassIndexForLabel(const double label) const
     {
      if(label==-1.0) return(0);
      if(label==0.0) return(1);
      if(label==1.0) return(2);
      return(-1);
     }

   double LabelForClassIndex(const int index) const
     {
      if(index==0) return(-1.0);
      if(index==1) return(0.0);
      if(index==2) return(1.0);
      return(EMPTY_VALUE);
     }

   bool ValidateProbabilities(const double sell_probability,
                              const double hold_probability,
                              const double buy_probability) const
     {
      const double total=sell_probability+hold_probability+buy_probability;
      return(sell_probability>=0.0 && sell_probability<=1.0 &&
             hold_probability>=0.0 && hold_probability<=1.0 &&
             buy_probability>=0.0 && buy_probability<=1.0 &&
             MathAbs(total-1.0)<0.000001);
     }

   bool IsValid(void) const
     {
      return(ModelName()!="" && ContractVersion()!="" &&
             FeatureCount()==12 && ClassCount()==3 &&
             FeatureName(0)=="trend_regime" && FeatureName(1)=="trend_momentum" &&
             FeatureName(2)=="trend_slope" && FeatureName(3)=="volatility_regime" &&
             FeatureName(4)=="volatility_change" && FeatureName(5)=="liquidity_activity" &&
             FeatureName(6)=="liquidity_range_position" &&
             FeatureName(7)=="liquidity_sweep_direction" &&
             FeatureName(8)=="session_asia" && FeatureName(9)=="session_london" &&
             FeatureName(10)=="session_new_york" && FeatureName(11)=="session_progress" &&
             ClassIndexForLabel(-1.0)==0 && ClassIndexForLabel(0.0)==1 &&
             ClassIndexForLabel(1.0)==2 &&
             ValidateProbabilities(0.0,1.0,0.0));
     }
  };

#endif
