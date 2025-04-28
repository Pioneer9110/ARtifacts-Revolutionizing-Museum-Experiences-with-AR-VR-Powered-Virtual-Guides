#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "FileBP.generated.h" // MUST be the last include!

UCLASS()
class FINAL_P_API UFileBP : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "External Execution")
    static bool RunExternalFile(
        const FString& FilePath,
        const FString& Parameters = TEXT(""),
        bool bLaunchDetached = true,
        bool bLaunchHidden = false,
        bool bLaunchReallyHidden = false
    );
};
