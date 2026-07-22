//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TrendAssembler.mqh                                     |
//| Layer   : Brain / Trend / Assembler                              |
//| Version : 4.4.0                                                  |
//| Purpose : Assemble Trend Analysis Result                         |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ASSEMBLER_TRENDASSEMBLER_MQH
#define CORE_BRAIN_TREND_ASSEMBLER_TRENDASSEMBLER_MQH

#include "../models/TrendResult.mqh"

#include "../../../indicators/models/EMAResult.mqh"

#include "../models/SlopeResult.mqh"
#include "../models/StructureResult.mqh"
#include "../models/BOSResult.mqh"
#include "../models/CHOCHResult.mqh"

//--------------------------------------------------

class CTrendAssembler
{
public:

   CTrendResult Assemble(
      const CEMAResult       &ema,
      const CSlopeResult     &slope,
      const CStructureResult &structure,
      const CBOSResult       &bos,
      const CCHOCHResult     &choch,
      const double            atr,
      const double            fast_ema_lookback)
   {
      CTrendResult result;

      //--------------------------------------------------
      // Direction
      //--------------------------------------------------

      if(ema.Bullish &&
         slope.Rising &&
         structure.ValidStructure)
      {
         result.Direction = TREND_BULLISH;
      }
      else
      if(ema.Bearish &&
         slope.Falling &&
         structure.ValidStructure)
      {
         result.Direction = TREND_BEARISH;
      }
      else
      {
         result.Direction = TREND_SIDEWAYS;
      }

      //--------------------------------------------------
      // Strength
      //--------------------------------------------------

      result.Strength = 0.0;

      if(ema.Bullish || ema.Bearish)
         result.Strength += 25.0;

      if(slope.Rising || slope.Falling)
         result.Strength += 25.0;

      if(structure.ValidStructure)
         result.Strength += 25.0;

      if(bos.ValidBreak)
         result.Strength += 25.0;

      if(result.Strength > 100.0)
         result.Strength = 100.0;

      //--------------------------------------------------
      // AI Trend Score
      // Continuous, multi-horizon ATR-normalized momentum for the AI feature path.
      // It deliberately leaves runtime Strength unchanged.
      //--------------------------------------------------

      result.AITrendScore=50.0;
      result.AITrendRegime=50.0;
      result.AITrendMomentum=50.0;
      result.AITrendSlope=50.0;
      if(atr>0.0 && ema.FastEMA!=ema.SlowEMA && fast_ema_lookback!=0.0)
        {
         const double regime_gap=ema.FastEMA-ema.SlowEMA;
         const double medium_move=ema.FastEMA-fast_ema_lookback;
         double regime_component=MathMax(-1.0,MathMin(1.0,regime_gap/(2.0*atr)));
         double medium_component=MathMax(-1.0,MathMin(1.0,medium_move/(2.0*atr)));
         double slope_component=MathMax(-1.0,MathMin(1.0,slope.Value/(0.25*atr)));
         if(choch.ValidCHOCH)
           {
            regime_component*=0.50;
            medium_component*=0.50;
            slope_component*=0.50;
           }
         result.AITrendRegime=50.0+(50.0*regime_component);
         result.AITrendMomentum=50.0+(50.0*medium_component);
         result.AITrendSlope=50.0+(50.0*slope_component);
         double composite=(0.45*regime_component)+
                          (0.40*medium_component)+
                          (0.15*slope_component);
         composite=MathMax(-1.0,MathMin(1.0,composite));
         result.AITrendScore=50.0+(50.0*composite);
         result.AITrendScore=MathMax(0.0,MathMin(100.0,result.AITrendScore));
        }

      //--------------------------------------------------
      // Confidence
      //--------------------------------------------------

      result.Confidence = result.Strength;

      if(choch.ValidCHOCH)
         result.Confidence *= 0.50;

      //--------------------------------------------------
      // Valid
      //--------------------------------------------------

      result.Valid =
         (result.Direction != TREND_SIDEWAYS);

      return result;
   }
};

#endif
