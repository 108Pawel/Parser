# frozen_string_literal: true

require_relative 'laboratory_test_result'

# a class used for parsing data read from file
class Parser
  NEGATIVES = %w[NEGATIVE NIL].freeze
  POSITIVES = ['POSITIVE', '+', '++'].freeze

  def initialize(file_path)
    file = File.open(file_path)
    index = 1
    single_result_from_file = []
    @results_from_file = []

    File.readlines(file).each do |line|
      if line.split('|').include?(index.to_s) # joining results based on index
        single_result_from_file << line.split('|')
      else
        @results_from_file << single_result_from_file
        single_result_from_file = []
        single_result_from_file << line.split('|')
        index += 1
      end
    end
    @results_from_file << single_result_from_file
  end

  def map_single_result(element)
    code = element[0][2]
    result = get_result(element[0][3])
    format = get_format(element[0][2])
    comment = get_comment(element)

    { code: code, result: result, format: format, comment: comment }
  end

  def get_result(result)
    begin
      return result if Float(result)
    rescue StandardError
      false
    end
    begin
      return result.float if Integer(result)
    rescue StandardError
      false
    end
    return -1.0 if NEGATIVES.include?(result)
    return -2.0 if POSITIVES.include?(result)
    return -3.0 if result == '+++'
  end

  def get_format(format)
    return 'boolean' if format.include?('A')
    return 'nil_3plus' if format.include?('B')
    return 'float' if format.include?('C')
  end

  def get_comment(element)
    comment = []
    element.each do |e|
      comment << "#{e[2]}\n" if e[0] == 'NTE'
    end
    comment.join if comment.length.positive?
  end

  def mapped_results
    laboratory_test_results = []

    @results_from_file.each do |element|
      result = map_single_result(element)
      laboratory_test_results << LaboratoryTestResult.new(result[:code], result[:result], result[:format],
                                                          result[:comment])
    end

    laboratory_test_results
  end
end
