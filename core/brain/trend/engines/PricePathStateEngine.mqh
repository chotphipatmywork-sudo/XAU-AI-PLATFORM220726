//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PricePathStateEngine.mqh                               |
//| Layer   : Brain / Trend / Engines / Research                     |
//| Version : 1.0.0                                                  |
//| Purpose : Measure bounded past-only 16-bar price-path state      |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ENGINES_PRICEPATHSTATEENGINE_MQH
#define CORE_BRAIN_TREND_ENGINES_PRICEPATHSTATEENGINE_MQH

#include "../models/PricePathStateResult.mqh"

class CPricePathStateEngine
  {
private:
   int Sign(const double value) const
     {
      if(value>0.0)
         return(1);
      if(value<0.0)
         return(-1);
      return(0);
     }

   double EncodeSignedUnit(const double value) const
     {
      return(MathMax(0.0,MathMin(100.0,50.0+50.0*value)));
     }

public:
   CPricePathStateResult Analyze(const double &closes[],
                                 const double &highs[],
                                 const double &lows[],
                                 const double atr) const
     {
      CPricePathStateResult result;
      if(ArraySize(closes)!=17 || ArraySize(highs)!=16 ||
         ArraySize(lows)!=16 || atr<=0.0)
         return(result);

      double changes[];
      ArrayResize(changes,16);
      double travel=0.0;
      int up_changes=0;
      int down_changes=0;
      for(int index=0; index<16; index++)
        {
         if(closes[index]<=0.0 || closes[index+1]<=0.0 ||
            highs[index]<=0.0 || lows[index]<=0.0 ||
            highs[index]<lows[index])
            return(result);
         changes[index]=closes[index]-closes[index+1];
         travel+=MathAbs(changes[index]);
         if(changes[index]>0.0)
            up_changes++;
         else if(changes[index]<0.0)
            down_changes++;
        }
      if(travel<=0.0 || up_changes+down_changes<=0)
         return(result);

      int longest_up=0;
      int longest_down=0;
      int current_up=0;
      int current_down=0;
      for(int index=15; index>=0; index--)
        {
         const int direction=Sign(changes[index]);
         if(direction>0)
           {
            current_up++;
            current_down=0;
            if(current_up>longest_up)
               longest_up=current_up;
           }
         else if(direction<0)
           {
            current_down++;
            current_up=0;
            if(current_down>longest_down)
               longest_down=current_down;
           }
         else
           {
            current_up=0;
            current_down=0;
           }
        }

      int same_sign=0;
      int opposite_sign=0;
      for(int index=0; index<15; index++)
        {
         const int first=Sign(changes[index]);
         const int second=Sign(changes[index+1]);
         if(first==0 || second==0)
            continue;
         if(first==second)
            same_sign++;
         else
            opposite_sign++;
        }

      double path_high=highs[0];
      double path_low=lows[0];
      double recent_high=highs[0];
      double recent_low=lows[0];
      double earlier_high=highs[8];
      double earlier_low=lows[8];
      for(int index=0; index<16; index++)
        {
         if(highs[index]>path_high)
            path_high=highs[index];
         if(lows[index]<path_low)
            path_low=lows[index];
         if(index<8)
           {
            if(highs[index]>recent_high)
               recent_high=highs[index];
            if(lows[index]<recent_low)
               recent_low=lows[index];
           }
         else
           {
            if(highs[index]>earlier_high)
               earlier_high=highs[index];
            if(lows[index]<earlier_low)
               earlier_low=lows[index];
           }
        }
      const double path_range=path_high-path_low;
      const double recent_range=recent_high-recent_low;
      const double earlier_range=earlier_high-earlier_low;
      if(path_range<=0.0 || recent_range<=0.0 || earlier_range<=0.0)
         return(result);

      result.PathDirectionalEfficiency=EncodeSignedUnit(
         (closes[0]-closes[16])/travel);
      result.UpCloseRatio=100.0*up_changes/(up_changes+down_changes);
      result.DirectionalRunBalance=EncodeSignedUnit(
         (double)(longest_up-longest_down)/16.0);
      if(same_sign+opposite_sign>0)
         result.ReturnSignPersistence=EncodeSignedUnit(
            (double)(same_sign-opposite_sign)/(same_sign+opposite_sign));
      result.PathTravelAtr=MathMax(0.0,MathMin(100.0,
         50.0*travel/(8.0*atr)));
      result.RangeEfficiency=MathMax(0.0,MathMin(100.0,
         100.0*path_range/travel));
      result.RangeExpansion=MathMax(0.0,MathMin(100.0,
         50.0*recent_range/earlier_range));
      result.Valid=true;
      return(result);
     }
  };

#endif
