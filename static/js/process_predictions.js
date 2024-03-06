function get_prediction(predictions, tagName)
{
    if (predictions)
    {
        for (i = 0; i < predictions.lenght; i++)
        {
            if (predictions[i]["tagName"] == tagName)
                return predictions[i]["probability"];
        }
    }
    return null;
}
