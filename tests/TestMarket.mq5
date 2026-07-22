//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestMarket.mq5                                         |
//+------------------------------------------------------------------+

#include "../core/market/MarketEngine.mqh"


CMarketEngine Market;



void OnStart()
{

    Print("=== TEST MARKET START ===");


    if(Market.Initialize()==false)
    {
        Print("Market Initialize Failed");
        return;
    }



    CMarketData Data = Market.GetData();

    CPriceSeriesModel Series = Market.GetPriceSeries();



    Print(
        "Bid = ",
        Data.Bid()
    );



    Print(
        "Open[0] = ",
        Series.Open[0]
    );



    Print(
        "High[0] = ",
        Series.High[0]
    );



    Print(
        "Low[0] = ",
        Series.Low[0]
    );



    Print(
        "Close[0] = ",
        Series.Close[0]
    );


    Print("=== TEST MARKET END ===");

}