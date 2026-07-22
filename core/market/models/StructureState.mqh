//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureState.mqh                                     |
//| Layer   : Market / Models                                        |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_MODELS_STRUCTURESTATE_MQH
#define CORE_MARKET_MODELS_STRUCTURESTATE_MQH


class CStructureState
{

public:

    // Trend Direction (ทิศทางแนวโน้ม)
    int Trend;


    // Structure Events (เหตุการณ์โครงสร้าง)

    bool BOS;

    bool CHOCH;


    // Last Swing Information (ข้อมูล Swing ล่าสุด)

    double LastHigh;

    double LastLow;


    datetime LastHighTime;

    datetime LastLowTime;


    // Reset State (รีเซ็ตสถานะ)

    void Reset()
    {
        Trend = 0;

        BOS = false;

        CHOCH = false;


        LastHigh = 0;

        LastLow = 0;


        LastHighTime = 0;

        LastLowTime = 0;
    }

};


#endif